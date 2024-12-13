# Copyright (c) 2024 the Eclipse BaSyx Authors
#
# This program and the accompanying materials are made available under the terms of the MIT License, available in
# the LICENSE file of this project.
#
# SPDX-License-Identifier: MIT
"""
.. _adapter.aasx:

Functionality for reading and writing AASX files according to "Specification of the Asset Administration Shell Part 5:
Package File Format (AASX) v3.0".
The AASX file format is built upon the Open Packaging Conventions (OPC; ECMA 376-2). We use the ``pyecma376_2`` library
for low level OPC reading and writing. It currently supports all required features except for embedded digital
signatures. The following codeblock contains the required imports and functions to use the adapter.

    .. code-block:: python

        from basyx import model # Shortcut to import aas_core3 which should be installed after installing requirements
        from basyx.aasx import AASXWriter
        from basyx.object_store import ObjectStore

        object_store: ObjectStore = ObjectStore()
        file_store = DictSupplementaryFileContainer()

        aas = model.AssetAdministrationShell(id='https://acplt.org/Simple_AAS',
                                            asset_information=model.AssetInformation(
                                             asset_kind=model.AssetKind.TYPE))

        with AASXWriter("./MyAASXPackage.aasx") as writer:

            writer.write_aas(aas_ids=['https://acplt.org/Simple_AAS'],
                     object_store=object_store,
                     file_store=file_store)
    ..


Writing and reading of AASX packages is performed through the :class:`~.AASXReader` and :class:`~.AASXWriter` classes.
Each instance of these classes wraps an existing AASX file resp. a file to be created and allows to read/write the
included AAS objects into/form :class:`ObjectStores <basyx.ObjectStore>`.
For handling of embedded supplementary files, this module provides the
:class:`~.AbstractSupplementaryFileContainer` class
interface and the :class:`~.DictSupplementaryFileContainer` implementation.
"""

import abc
import hashlib
import io
import itertools
import logging
import os
import re
import contextlib
import json

from typing import (Dict, Tuple, IO, Union, List, Set, Optional, Iterable, BinaryIO, TextIO, Any, Callable,
                    Iterator, ContextManager, TypeVar, get_args, Type)

from aas_core3.types import HasSemantics
from basyx.object_store import ObjectStore
from aas_core3 import types as model
import pyecma376_2
import aas_core3.jsonization as aas_jsonization
from lxml import etree
import aas_core3.xmlization as aas_xmlization


logger = logging.getLogger(__name__)

RELATIONSHIP_TYPE_AASX_ORIGIN = "http://admin-shell.io/aasx/relationships/aasx-origin"
RELATIONSHIP_TYPE_AAS_SPEC = "http://admin-shell.io/aasx/relationships/aas-spec"
RELATIONSHIP_TYPE_AAS_SPEC_SPLIT = "http://admin-shell.io/aasx/relationships/aas-spec-split"
RELATIONSHIP_TYPE_AAS_SUPL = "http://admin-shell.io/aasx/relationships/aas-suppl"


# type aliases for path-like objects and IO
# used by parse_obj_store_to_xml, parse_xml_to_obj_store, parse_obj_store_to_json, parse_json_to_obj_store
Path = Union[str, bytes, os.PathLike]
PathOrBinaryIO = Union[Path, BinaryIO]
PathOrIO = Union[Path, IO]  # IO is TextIO or BinaryIO

# XML Namespace definition
XML_NS_MAP = {"aas": "https://admin-shell.io/aas/3/0"}
XML_NS_AAS = "{" + XML_NS_MAP["aas"] + "}"
NS_AAS = XML_NS_AAS

# type aliases
REQUIRED_NAMESPACES: Set[str] = {XML_NS_MAP["aas"]}
RE = TypeVar("RE", bound=model.RelationshipElement)
T = TypeVar('T')
id_type = str


class AASXReader:
    """
    An AASXReader wraps an existing AASX package file to allow reading its contents and metadata.

    Basic usage:

    .. code-block:: python

        objects = DictObjectStore()
        files = DictSupplementaryFileContainer()
        with AASXReader("filename.aasx") as reader:
            meta_data = reader.get_core_properties()
            reader.read_into(objects, files)

    """

    def __init__(self, file: Union[os.PathLike, str, IO]):
        """
        Open an AASX reader for the given filename or file handle

        The given file is opened as OPC ZIP package. Make sure to call ``AASXReader.close()`` after reading the file
        contents to close the underlying ZIP file reader. You may also use the AASXReader as a context manager to ensure
        closing under any circumstances.

        :param file: A filename, file path or an open file-like object in binary mode
        :raises FileNotFoundError: If the file does not exist
        :raises ValueError: If the file is not a valid OPC zip package
        """
        try:
            logger.debug("Opening {} as AASX pacakge for reading ...".format(file))
            self.reader = pyecma376_2.ZipPackageReader(file)
        except FileNotFoundError:
            raise
        except Exception as e:
            raise ValueError("{} is not a valid ECMA376-2 (OPC) file: {}".format(file, e)) from e

    def get_core_properties(self) -> pyecma376_2.OPCCoreProperties:
        """
        Retrieve the OPC Core Properties (meta data) of the AASX package file.

        If no meta data is provided in the package file, an emtpy OPCCoreProperties object is returned.

        :return: The AASX package's meta data
        """
        return self.reader.get_core_properties()

    def get_thumbnail(self) -> Optional[bytes]:
        """
        Retrieve the packages thumbnail image

        The thumbnail image file is read into memory and returned as bytes object. You may use some python image library
        for further processing or conversion, e.g. ``pillow``:

        .. code-block:: python

            import io
            from PIL import Image
            thumbnail = Image.open(io.BytesIO(reader.get_thumbnail()))

        :return: The AASX package thumbnail's file contents or None if no thumbnail is provided
        """
        try:
            thumbnail_part = self.reader.get_related_parts_by_type()[pyecma376_2.RELATIONSHIP_TYPE_THUMBNAIL][0]
        except IndexError:
            return None

        with self.reader.open_part(thumbnail_part) as p:
            return p.read()

    def read_into(self, object_store: ObjectStore,
                  file_store: "AbstractSupplementaryFileContainer",
                  replace_existing: bool = False, **kwargs) -> Set[id_type]:
        """
        Read the contents of the AASX package and add them into a given
        :class:`ObjectStore <basyx.ObjectStore>`

        This function does the main job of reading the AASX file's contents. It traverses the relationships within the
        package to find AAS JSON or XML parts, parses them and adds the contained AAS objects into the provided
        ``object_store``. While doing so, it searches all parsed :class:`Submodels <aas_core3.types.Submodel>`
        for :class:`~aas_core3.types.File` objects to extract the supplementary files. The referenced
        supplementary files are added to the given ``file_store`` and the :class:`~aas_core3.types.File`
        objects' values are updated with the absolute name of the supplementary file to allow for robust resolution the
        file within the ``file_store`` later.

        :param object_store: An :class:`ObjectStore <basyx.ObjectStore>` to add the AAS
                             objects from the AASX file to
        :param file_store: A :class:`SupplementaryFileContainer <.AbstractSupplementaryFileContainer>` to add the
                           embedded supplementary files to
        :param replace_existing: If ``True``, existing objects in the object store are overridden with objects from the
            AASX that have the same Identifier. Default behavior is to skip those objects
            from the AASX.
        :return: A set of the Identifiers of all
                 :class:`~aas_core3.types.Identifiable` objects parsed from the AASX file
        """
        # Find AASX-Origin part
        core_rels = self.reader.get_related_parts_by_type()
        try:
            aasx_origin_part = core_rels[RELATIONSHIP_TYPE_AASX_ORIGIN][0]
        except IndexError as e:
            raise ValueError("Not a valid AASX file: aasx-origin Relationship is missing.") from e

        read_identifiables: Set[id_type] = set()
        # Iterate AAS files
        for aas_part in self.reader.get_related_parts_by_type(aasx_origin_part)[RELATIONSHIP_TYPE_AAS_SPEC]:
            self._read_aas_part_into(aas_part, object_store, file_store,
                                     read_identifiables, replace_existing, **kwargs)

            # Iterate split parts of AAS file
            for split_part in self.reader.get_related_parts_by_type(aas_part)[RELATIONSHIP_TYPE_AAS_SPEC_SPLIT]:
                self._read_aas_part_into(split_part, object_store, file_store,
                                         read_identifiables, replace_existing, **kwargs)

        return read_identifiables

    def close(self) -> None:
        """
        Close the AASXReader and the underlying OPC / ZIP file readers. Must be called after reading the file.
        """
        self.reader.close()

    def __enter__(self) -> "AASXReader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _read_aas_part_into(self, part_name: str,
                            object_store: ObjectStore,
                            file_store: "AbstractSupplementaryFileContainer",
                            read_identifiables: Set[id_type],
                            replace_existing: bool, **kwargs) -> None:
        """
        Helper function for :meth:`read_into()` to read and process the contents of an AAS-spec part of the AASX file.


        :param part_name: The OPC part name to read
        :param object_store: An ObjectStore to add the AAS objects from the AASX file to
        :param file_store: A SupplementaryFileContainer to add the embedded supplementary files to, which are reference
            from a File object of this part
        :param read_identifiables: A set of Identifiers of objects which have already been read. New objects'
            Identifiers are added to this set. Objects with already known Identifiers are skipped silently.
        :param replace_existing: If True, existing objects in the object store are overridden with objects from the
            AASX that have the same Identifer. Default behavior is to skip those objects from the AASX.
        """

        for obj in self._parse_aas_part(part_name, **kwargs):
            if obj.id in read_identifiables:
                continue
            if obj.id in object_store:
                if replace_existing:
                    logger.info("Overriding existing object in  ObjectStore with {} ...".format(obj.id))
                    existing_object = object_store.get(obj.id)
                    object_store.discard(existing_object)

                else:
                    logger.warning("Skipping {}, since an object with the same id is already contained in the "
                                   "ObjectStore".format(obj.id))
                    continue
            object_store.add(obj)
            read_identifiables.add(obj.id)
            if isinstance(obj, model.Submodel):
                self._collect_supplementary_files(part_name, obj, file_store)

    def _parse_aas_part(self, part_name: str, **kwargs) -> ObjectStore:
        """
        Helper function to parse the AAS objects from a single JSON or XML part of the AASX package.

        This method chooses and calls the correct parser.

        :param part_name: The OPC part name of the part to be parsed
        :return: An ObjectStore containing the parsed AAS objects
        """

        content_type = self.reader.get_content_type(part_name)
        extension = part_name.split("/")[-1].split(".")[-1]
        if content_type.split(";")[0] in ("text/xml", "application/xml") or content_type == "" and extension == "xml":
            logger.debug("Parsing AAS objects from XML stream in OPC part {} ...".format(part_name))
            with self.reader.open_part(part_name) as p:
                return parse_xml_to_obj_store(p, **kwargs)
        elif content_type.split(";")[0] in ("text/json", "application/json") \
                or content_type == "" and extension == "json":
            logger.debug("Parsing AAS objects from JSON stream in OPC part {} ...".format(part_name))

            with self.reader.open_part(part_name) as p:
                return parse_json_to_obj_store(io.TextIOWrapper(p, encoding='utf-8-sig'), **kwargs)
        else:
            logger.error("Could not determine part format of AASX part {} (Content Type: {}, extension: {}"
                         .format(part_name, content_type, extension))
            return ObjectStore()

    def _collect_supplementary_files(self, part_name: str, submodel: model.Submodel,
                                     file_store: "AbstractSupplementaryFileContainer") -> None:
        """
        Helper function to search File objects within a single parsed Submodel, extract the referenced supplementary
        files and update the File object's values with the absolute path.

        :param part_name: The OPC part name of the part the submodel has been parsed from. This is used to resolve
            relative file paths.
        :param submodel: The Submodel to process
        :param file_store: The SupplementaryFileContainer to add the extracted supplementary files to
        """
        for element in submodel.descend():
            if isinstance(element, model.File):
                if element.value is None:
                    continue
                # Only absolute-path references and relative-path URI references (see RFC 3986, sec. 4.2) are considered
                # to refer to files within the AASX package. Thus, we must skip all other types of URIs (esp. absolute
                # URIs and network-path references)
                if element.value.startswith('//') or ':' in element.value.split('/')[0]:
                    logger.info("Skipping supplementary file %s, since it seems to be an absolute URI or network-path "
                                "URI reference", element.value)
                    continue
                absolute_name = pyecma376_2.package_model.part_realpath(element.value, part_name)
                logger.debug("Reading supplementary file {} from AASX package ...".format(absolute_name))
                with self.reader.open_part(absolute_name) as p:
                    final_name = file_store.add_file(absolute_name, p, self.reader.get_content_type(absolute_name))
                element.value = final_name


class AASXWriter:
    """
    An AASXWriter wraps a new AASX package file to write its contents to it piece by piece.

    Basic usage:

    .. code-block:: python

        # object_store and file_store are expected to be given (e.g. some storage backend or previously created data)
        cp = OPCCoreProperties()
        cp.creator = "ACPLT"
        cp.created = datetime.datetime.now()

        with AASXWriter("filename.aasx") as writer:
            writer.write_aas("https://acplt.org/AssetAdministrationShell",
                             object_store,
                             file_store)
            writer.write_aas("https://acplt.org/AssetAdministrationShell2",
                             object_store,
                             file_store)
            writer.write_core_properties(cp)

    .. attention::

        The AASXWriter must always be closed using the :meth:`~.AASXWriter.close` method or its context manager
        functionality (as shown above). Otherwise, the resulting AASX file will lack important data structures
        and will not be readable.
    """
    AASX_ORIGIN_PART_NAME = "/aasx/aasx-origin"

    def __init__(self, file: Union[os.PathLike, str, IO]):
        """
        Create a new AASX package in the given file and open the AASXWriter to add contents to the package.

        Make sure to call ``AASXWriter.close()`` after writing all contents to write the aas-spec relationships for all
        AAS parts to the file and close the underlying ZIP file writer. You may also use the AASXWriter as a context
        manager to ensure closing under any circumstances.

        :param file: filename, path, or binary file handle opened for writing
        """
        # names of aas-spec parts, used by `_write_aasx_origin_relationships()`
        self._aas_part_names: List[str] = []
        # name of the thumbnail part (if any)
        self._thumbnail_part: Optional[str] = None
        # name of the core properties part (if any)
        self._properties_part: Optional[str] = None
        # names and hashes of all supplementary file parts that have already been written
        self._supplementary_part_names: Dict[str, Optional[bytes]] = {}

        # Open OPC package writer
        self.writer = pyecma376_2.ZipPackageWriter(file)

        # Create AASX origin part
        logger.debug("Creating AASX origin part in AASX package ...")
        p = self.writer.open_part(self.AASX_ORIGIN_PART_NAME, "text/plain")
        p.close()

    def write_aas(self,
                  aas_ids: List[id_type],
                  object_store: ObjectStore,
                  file_store: "AbstractSupplementaryFileContainer",
                  write_json: bool = False) -> None:
        """
        Convenience method to write one or more
        :class:`AssetAdministrationShells` with all included
        and referenced objects to the AASX package according to the part name conventions from DotAAS.

        This method takes the AASs' Identifiers (as ``aas_ids``) to retrieve
        the AASs from the given ``object_store``.
        :class:`References` to :class:`Submodels` and :class:`ConceptDescriptions` (via semanticId attributes) are
        also resolved using the ``object_store``. All of these objects are written to an aas-spec part
        ``/aasx/data.xml`` or ``/aasx/data.json`` in the AASX package, compliant to the convention presented in
        "Details of the Asset Administration Shell". Supplementary files which are referenced by a
        :class:`aas_core3.type.File` object in any of the
        :class:`Submodels` are also added to the AASX package.

        This method uses :meth:`write_all_aas_objects` to write the AASX part.

        .. attention::

            This method **must only be used once** on a single AASX package. Otherwise, the ``/aasx/data.json``
            (or ``...xml``) part would be written twice to the package, hiding the first part and possibly causing
            problems when reading the package.

            To write multiple Asset Administration Shells to a single AASX package file, call this method once, passing
            a list of AAS Identifiers to the ``aas_ids`` parameter.

        :param aas_ids: :class:`~aas_core3.types.Identifiable` or Iterable of
            :class:`Identifiers <aas_core3.types.Identifiable.id>` of the AAS(s) to be written to the AASX file
        :param object_store: :class:`ObjectStore <basyx.ObjectStore>` to retrieve the
            :class:`~aas_core3.types.Identifiable` AAS objects
            (:class:`~aas_core3.types.Assetadministrationshell`,
            :class:`~~aas_core3.types.ConceptDescription` and :class:`~aas_core3.types.Submodel`) from
        :param file_store: :class:`SupplementaryFileContainer <AbstractSupplementaryFileContainer>` to retrieve
            supplementary files from, which are referenced by :class:`~aas_core3.types.File` objects
        :param write_json:  If ``True``, JSON parts are created for the AAS and each
            :class:`~aas_core3.types.Submodel` in the AASX package file instead of XML parts.
            Defaults to ``False``.
        :raises KeyError: If one of the AAS could not be retrieved from the object store
        :raises TypeError: If one of the given AAS ids does not resolve to an AAS (but another
            Identifiable object)
        """

        objects_to_be_written: ObjectStore[model.Identifiable] = ObjectStore()
        for aas_id in aas_ids:
            try:
                aas: model.AssetAdministrationShell = object_store.get_identifiable(aas_id)
            # TODO add failsafe mode
            except KeyError:
                raise
            if not isinstance(aas, model.AssetAdministrationShell):
                raise TypeError(f"Identifier {aas_id} does not belong to an AssetAdminstrationShell object but to "
                                f"{aas!r}")
            # Add the AssetAdministrationShell object to the data part
            objects_to_be_written.add(aas)

            # Add referenced Submodels to the data part
            if aas.submodels is not None:

                for submodel_ref in aas.submodels:
                    try:
                        submodel_keys = submodel_ref.keys
                        for key in submodel_keys:
                            submodel_id = key.value
                            try:
                                submodel = object_store.get_identifiable(submodel_id)
                            except Exception:
                                continue
                            objects_to_be_written.add(submodel)

                    except KeyError:
                        logger.warning("Could not find submodel %s. Skipping it.", str(submodel_ref))
                        continue

        # Traverse object tree and check if semanticIds are referencing to existing ConceptDescriptions in the
        # ObjectStore
        concept_descriptions: List[model.ConceptDescription] = []
        for identifiable in objects_to_be_written:
            for element in identifiable.descend():
                if isinstance(element, HasSemantics):

                    semantic_id = element.semantic_id
                    if semantic_id is not None:
                        for key in semantic_id.keys:
                            cd = object_store.get_identifiable(key.value)
                            concept_descriptions.append(cd)

        for element in concept_descriptions:
            objects_to_be_written.add(element)

        # Write AAS data part
        self.write_all_aas_objects("/aasx/data.{}".format("json" if write_json else "xml"),
                                   objects_to_be_written, file_store, write_json)

    # TODO remove `split_part` parameter in future version.
    #   Not required anymore since changes from DotAAS version 2.0.1 to 3.0RC01

    def write_all_aas_objects(self,
                              part_name: str,
                              objects: ObjectStore,
                              file_store: "AbstractSupplementaryFileContainer",
                              write_json: bool = False,
                              split_part: bool = False,
                              additional_relationships: Iterable[pyecma376_2.OPCRelationship] = ()) -> None:
        """
        Write all AAS objects in a given :class:`ObjectStore <basyx.ObjectStore>` to an XML
        or JSON part in the AASX package and add the referenced supplementary files to the package.

        This method takes a :class:`ObjectStore <basyx.ObjectStore>` and writes all
        contained objects into an ``aas_env`` part in the AASX package. If the ObjectStore includes
        :class:`~aas_core3.types.Submodel` objects, supplementary files which are referenced by
        :class:`~aas_core3.types.submodel.File` objects within those Submodels, are fetched from the ``file_store``
        and added to the AASX package.

        .. attention::

            You must make sure to call this method only once per unique ``part_name`` on a single package instance.

        :param part_name: Name of the Part within the AASX package to write the files to. Must be a valid ECMA376-2
            part name and unique within the package. The extension of the part should match the data format (i.e.
            '.json' if ``write_json`` else '.xml').
        :param objects: The objects to be written to the AASX package. Only these Identifiable objects (and included
            Referable objects) are written to the package.
        :param file_store: The SupplementaryFileContainer to retrieve supplementary files from (if there are any
            ``File`` objects within the written objects.
        :param write_json: If True, the part is written as a JSON file instead of an XML file. Defaults to False.
        :param split_part: If True, no aas-spec relationship is added from the aasx-origin to this part. You must make
            sure to reference it via a aas-spec-split relationship from another aas-spec part
        :param additional_relationships: Optional OPC/ECMA376 relationships which should originate at the AAS object
            part to be written, in addition to the aas-suppl relationships which are created automatically.
        """
        logger.debug("Writing AASX part {} with AAS objects ...".format(part_name))
        supplementary_files: List[str] = []

        # Retrieve objects and scan for referenced supplementary files
        for the_object in objects:
            if isinstance(the_object, model.Submodel):
                for element in the_object.descend():
                    if isinstance(element, model.File):
                        file_name = element.value
                        # Skip File objects with empty value URI references that are considered to be no local file
                        # (absolute URIs or network-path URI references)
                        if file_name is None or file_name.startswith('//') or ':' in file_name.split('/')[0]:
                            continue
                        supplementary_files.append(file_name)

        # Add aas-spec relationship
        if not split_part:
            self._aas_part_names.append(part_name)

        # Write part
        # TODO allow writing xml *and* JSON part
        with self.writer.open_part(part_name, "application/json" if write_json else "application/xml") as p:
            if write_json:
                parse_obj_store_to_json(io.TextIOWrapper(p, encoding='utf-8'), objects)
            else:
                parse_obj_store_to_xml(p, objects)

        # Write submodel's supplementary files to AASX file
        supplementary_file_names = []
        for file_name in supplementary_files:
            try:
                content_type = file_store.get_content_type(file_name)
                hash = file_store.get_sha256(file_name)
            except KeyError:
                logger.warning("Could not find file {} in file store.".format(file_name))
                continue
            # Check if this supplementary file has already been written to the AASX package or has a name conflict
            if self._supplementary_part_names.get(file_name) == hash:
                continue
            elif file_name in self._supplementary_part_names:
                logger.error("Trying to write supplementary file {} to AASX twice with different contents"
                             .format(file_name))
            logger.debug("Writing supplementary file {} to AASX package ...".format(file_name))
            with self.writer.open_part(file_name, content_type) as p:
                file_store.write_file(file_name, p)
            supplementary_file_names.append(pyecma376_2.package_model.normalize_part_name(file_name))
            self._supplementary_part_names[file_name] = hash

        # Add relationships from submodel to supplementary parts
        logger.debug("Writing aas-suppl relationships for AAS object part {} to AASX package ...".format(part_name))
        self.writer.write_relationships(
            itertools.chain(
                (pyecma376_2.OPCRelationship("r{}".format(i),
                                             RELATIONSHIP_TYPE_AAS_SUPL,
                                             submodel_file_name,
                                             pyecma376_2.OPCTargetMode.INTERNAL)
                 for i, submodel_file_name in enumerate(supplementary_file_names)),
                additional_relationships),
            part_name)

    def write_core_properties(self, core_properties: pyecma376_2.OPCCoreProperties):
        """
        Write OPC Core Properties (meta data) to the AASX package file.

        .. Attention::
            This method may only be called once for each AASXWriter!

        :param core_properties: The OPCCoreProperties object with the meta data to be written to the package file
        """
        if self._properties_part is not None:
            raise RuntimeError("Core Properties have already been written.")
        logger.debug("Writing core properties to AASX package ...")
        with self.writer.open_part(pyecma376_2.DEFAULT_CORE_PROPERTIES_NAME, "application/xml") as p:
            core_properties.write_xml(p)
        self._properties_part = pyecma376_2.DEFAULT_CORE_PROPERTIES_NAME

    def write_thumbnail(self, name: str, data: bytearray, content_type: str):
        """
        Write an image file as thumbnail image to the AASX package.

        .. Attention::
            This method may only be called once for each AASXWriter!

        :param name: The OPC part name of the thumbnail part. Should not contain '/' or URI-encoded '/' or '\'.
        :param data: The image file's binary contents to be written
        :param content_type: OPC content type (MIME type) of the image file
        """
        if self._thumbnail_part is not None:
            raise RuntimeError("package thumbnail has already been written to {}.".format(self._thumbnail_part))
        with self.writer.open_part(name, content_type) as p:
            p.write(data)
        self._thumbnail_part = name

    def close(self):
        """
        Write relationships for all data files to package and close underlying OPC package and ZIP file.
        """
        self._write_aasx_origin_relationships()
        self._write_package_relationships()
        self.writer.close()

    def __enter__(self) -> "AASXWriter":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def _write_aasx_origin_relationships(self):
        """
        Helper function to write aas-spec relationships of the aasx-origin part.

        This method uses the list of aas-spec parts in ``_aas_part_names``. It should be called just before closing the
        file to make sure all aas-spec parts of the package have already been written.
        """
        # Add relationships from AASX-origin part to AAS parts
        logger.debug("Writing aas-spec relationships to AASX package ...")
        self.writer.write_relationships(
            (pyecma376_2.OPCRelationship("r{}".format(i), RELATIONSHIP_TYPE_AAS_SPEC,
                                         aas_part_name,
                                         pyecma376_2.OPCTargetMode.INTERNAL)
             for i, aas_part_name in enumerate(self._aas_part_names)),
            self.AASX_ORIGIN_PART_NAME)

    def _write_package_relationships(self):
        """
        Helper function to write package (root) relationships to the OPC package.

        This method must be called just before closing the package file to make sure we write exactly the correct
        relationships:
        * aasx-origin (always)
        * core-properties (if core properties have been added)
        * thumbnail (if thumbnail part has been added)
        """
        logger.debug("Writing package relationships to AASX package ...")
        package_relationships: List[pyecma376_2.OPCRelationship] = [
            pyecma376_2.OPCRelationship("r1", RELATIONSHIP_TYPE_AASX_ORIGIN,
                                        self.AASX_ORIGIN_PART_NAME,
                                        pyecma376_2.OPCTargetMode.INTERNAL),
        ]
        if self._properties_part is not None:
            package_relationships.append(pyecma376_2.OPCRelationship(
                "r2", pyecma376_2.RELATIONSHIP_TYPE_CORE_PROPERTIES, self._properties_part,
                pyecma376_2.OPCTargetMode.INTERNAL))
        if self._thumbnail_part is not None:
            package_relationships.append(pyecma376_2.OPCRelationship(
                "r3", pyecma376_2.RELATIONSHIP_TYPE_THUMBNAIL, self._thumbnail_part,
                pyecma376_2.OPCTargetMode.INTERNAL))
        self.writer.write_relationships(package_relationships)


class AbstractSupplementaryFileContainer(metaclass=abc.ABCMeta):
    """
    Abstract interface for containers of supplementary files for AASs.

    Supplementary files may be PDF files or other binary or textual files, referenced in a File object of an AAS by
    their name. They are used to provide associated documents without embedding their contents (as
    :class:`~aas_core3.types.Blob` object) in the AAS.

    A SupplementaryFileContainer keeps track of the name and content_type (MIME type) for each file. Additionally it
    allows to resolve name conflicts by comparing the files' contents and providing an alternative name for a dissimilar
    new file. It also provides each files sha256 hash sum to allow name conflict checking in other classes (e.g. when
    writing AASX files).
    """

    @abc.abstractmethod
    def add_file(self, name: str, file: IO[bytes], content_type: str) -> str:
        """
        Add a new file to the SupplementaryFileContainer and resolve name conflicts.

        The file contents must be provided as a binary file-like object to be read by the SupplementaryFileContainer.
        If the container already contains an equally named file, the content_type and file contents are compared (using
        a hash sum). In case of dissimilar files, a new unique name for the new file is computed and returned. It should
        be used to update in the File object of the AAS.

        :param name: The file's proposed name. Should start with a '/'. Should not contain URI-encoded '/' or '\'
        :param file: A binary file-like opened for reading the file contents
        :param content_type: The file's content_type
        :return: The file name as stored in the SupplementaryFileContainer. Typically ``name`` or a modified version of
            ``name`` to resolve conflicts.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_content_type(self, name: str) -> str:
        """
        Get a stored file's content_type.

        :param name: file name of questioned file
        :return: The file's content_type
        :raises KeyError: If no file with this name is stored
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def get_sha256(self, name: str) -> bytes:
        """
        Get a stored file content's sha256 hash sum.

        This may be used by other classes (e.g. the AASXWriter) to check for name conflicts.

        :param name: file name of questioned file
        :return: The file content's sha256 hash sum
        :raises KeyError: If no file with this name is stored
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def write_file(self, name: str, file: IO[bytes]) -> None:
        """
        Retrieve a stored file's contents by writing them into a binary writable file-like object.

        :param name: file name of questioned file
        :param file: A binary file-like object with write() method to write the file contents into
        :raises KeyError: If no file with this name is stored
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def delete_file(self, name: str) -> None:
        """
        Deletes a file from this SupplementaryFileContainer given its name.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def __contains__(self, item: str) -> bool:
        """
        Check if a file with the given name is stored in this SupplementaryFileContainer.
        """
        pass  # pragma: no cover

    @abc.abstractmethod
    def __iter__(self) -> Iterator[str]:
        """
        Return an iterator over all file names stored in this SupplementaryFileContainer.
        """
        pass  # pragma: no cover


class DictSupplementaryFileContainer(AbstractSupplementaryFileContainer):
    """
    SupplementaryFileContainer implementation using a dict to store the file contents in-memory.
    """

    def __init__(self):
        # Stores the files' contents, identified by their sha256 hash
        self._store: Dict[bytes, bytes] = {}
        # Maps file names to (sha256, content_type)
        self._name_map: Dict[str, Tuple[bytes, str]] = {}
        # Tracks the number of references to _store keys,
        # i.e. the number of different filenames referring to the same file
        self._store_refcount: Dict[bytes, int] = {}

    def add_file(self, name: str, file: IO[bytes], content_type: str) -> str:
        data = file.read()
        hash = hashlib.sha256(data).digest()
        if hash not in self._store:
            self._store[hash] = data
            self._store_refcount[hash] = 0
        name_map_data = (hash, content_type)
        new_name = name
        i = 1
        while True:
            if new_name not in self._name_map:
                self._name_map[new_name] = name_map_data
                self._store_refcount[hash] += 1
                return new_name
            elif self._name_map[new_name] == name_map_data:
                return new_name
            new_name = self._append_counter(name, i)
            i += 1

    @staticmethod
    def _append_counter(name: str, i: int) -> str:
        split1 = name.split('/')
        split2 = split1[-1].split('.')
        index = -2 if len(split2) > 1 else -1
        new_basename = "{}_{:04d}".format(split2[index], i)
        split2[index] = new_basename
        split1[-1] = ".".join(split2)
        return "/".join(split1)

    def get_content_type(self, name: str) -> str:
        return self._name_map[name][1]

    def get_sha256(self, name: str) -> bytes:
        return self._name_map[name][0]

    def write_file(self, name: str, file: IO[bytes]) -> None:
        file.write(self._store[self._name_map[name][0]])

    def delete_file(self, name: str) -> None:
        # The number of different files with the same content are kept track of via _store_refcount.
        # The contents are only deleted, once the refcount reaches zero.
        hash: bytes = self._name_map[name][0]
        self._store_refcount[hash] -= 1
        if self._store_refcount[hash] == 0:
            del self._store[hash]
            del self._store_refcount[hash]
        del self._name_map[name]

    def __contains__(self, item: object) -> bool:
        return item in self._name_map

    def __iter__(self) -> Iterator[str]:
        return iter(self._name_map)


def parse_json_to_obj_store(file: PathOrIO) -> ObjectStore[model.Identifiable]:
    """
    Read an Asset Administration Shell JSON file according to 'Details of the Asset Administration Shell', chapter 5.5
    into a given object store.

    :param file: A filename or file-like object to read the JSON-serialized data from
    :raises KeyError: Encountered a duplicate identifier
    :raises KeyError: Encountered an identifier that already exists in the given ``object_store`` with both
                     ``replace_existing`` and ``ignore_existing`` set to ``False``
    :raises TypeError: **Non-failsafe**: Encountered an element in the wrong list
                                         (e.g. an AssetAdministrationShell in ``submodels``)
    :return: A set of :class:`Identifiers <basyx.aas.model.base.Identifier>` that were added to object_store
    """
    object_store: ObjectStore[model.Identifiable] = ObjectStore()

    ret: Set[str] = set()
    # json.load() accepts TextIO and BinaryIO
    cm: ContextManager[IO]
    if isinstance(file, get_args(Path)):
        # 'file' is a path, needs to be opened first
        cm = open(file, "r", encoding="utf-8-sig")
    else:
        # 'file' is not a path, thus it must already be IO
        # mypy seems to have issues narrowing the type due to get_args()
        cm = contextlib.nullcontext(file)  # type: ignore[arg-type]

    # read, parse and convert JSON file
    with cm as fp:
        data = json.load(fp)

    for name, expected_type in (('assetAdministrationShells', model.AssetAdministrationShell),
                                ('submodels', model.Submodel),
                                ('conceptDescriptions', model.ConceptDescription)):
        try:
            lst: list = data[name]
        except (KeyError, TypeError):
            continue

        for item in lst:
            identifiable = aas_jsonization.identifiable_from_jsonable(item)
            if identifiable.id in ret:
                error_message = f"{item} has a duplicate identifier already parsed in the document!"
                raise KeyError(error_message)

            object_store.add(identifiable)
            ret.add(identifiable.id)

    return object_store


def parse_obj_store_to_json(file: PathOrIO, data: ObjectStore, **kwargs) -> None:
    """
    Write a set of AAS objects to an Asset Administration Shell JSON file according to 'Details of the Asset
    Administration Shell', chapter 5.5

    :param file: A filename or file-like object to write the JSON-serialized data to
    :param data: :class:`ObjectStore <basyx.aas.model.provider.AbstractObjectStore>` which contains different objects of
                 the AAS meta model which should be serialized to a JSON file
    :param kwargs: Additional keyword arguments to be passed to `json.dump()`
    """

    # json.dump() only accepts TextIO
    cm: ContextManager[TextIO]
    if isinstance(file, get_args(Path)):
        # 'file' is a path, needs to be opened first
        cm = open(file, "w", encoding="utf-8")
    elif not hasattr(file, "encoding"):
        # only TextIO has this attribute, so this must be BinaryIO, which needs to be wrapped
        # mypy seems to have issues narrowing the type due to get_args()
        cm = _DetachingTextIOWrapper(file, "utf-8", write_through=True)  # type: ignore[arg-type]
    else:
        # we already got TextIO, nothing needs to be done
        # mypy seems to have issues narrowing the type due to get_args()
        cm = contextlib.nullcontext(file)  # type: ignore[arg-type]

    # serialize object to json#
    asset_administration_shells: List = []
    submodels: List = []
    concept_descriptions: List = []
    for obj in data:
        if isinstance(obj, model.AssetAdministrationShell):
            asset_administration_shells.append(aas_jsonization.to_jsonable(obj))
        elif isinstance(obj, model.Submodel):
            submodels.append(aas_jsonization.to_jsonable(obj))
        elif isinstance(obj, model.ConceptDescription):
            concept_descriptions.append(aas_jsonization.to_jsonable(obj))
    dict_: Dict[str, List] = {}
    if asset_administration_shells:
        dict_['assetAdministrationShells'] = asset_administration_shells
    if submodels:
        dict_['submodels'] = submodels
    if concept_descriptions:
        dict_['conceptDescriptions'] = concept_descriptions

    with cm as fp:
        json.dump(dict_, fp, **kwargs)


def parse_xml_to_obj_store(file: PathOrIO, **parser_kwargs) -> ObjectStore[model.Identifiable]:
    """
    Able to parse the official schema files into a given
    :class:`ObjectStore <basyx.aas.model.provider.AbstractObjectStore>`.

    :param file: A filename or file-like object to read the XML-serialized data from
    :raises ~lxml.etree.XMLSyntaxError: If the given file(-handle) has invalid XML
    :raises KeyError: If a required namespace has not been declared on the XML document
    :raises KeyError: Encountered a duplicate identifier
    :raises KeyError: Encountered an identifier that already exists in the given ``object_store`` with both
                     ``replace_existing`` and ``ignore_existing`` set to ``False``
    :raises (~basyx.aas.model.base.AASConstraintViolation, KeyError, ValueError): Errors during
                                                                                  construction of the objects
    :raises TypeError: Encountered an undefined top-level list (e.g. ``<aas:submodels1>``)
    :return: A set of :class:`Identifiers <basyx.aas.model.base.Identifier>` that were added to object_store
    """
    object_store: ObjectStore = ObjectStore()
    ret: Set = set()

    element_constructors: Dict[str, Callable[..., model.Identifiable]] = {
        "assetAdministrationShell": aas_xmlization.asset_administration_shell_from_str,
        "conceptDescription": aas_xmlization.concept_description_from_str,
        "submodel": aas_xmlization.submodel_from_str
    }

    element_constructors = {NS_AAS + k: v for k, v in element_constructors.items()}
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True, **parser_kwargs)

    root = etree.parse(file, parser).getroot()

    if root is None:
        return object_store
    # Add AAS objects to ObjectStore
    for list_ in root:

        element_tag = list_.tag[:-1]
        if list_.tag[-1] != "s" or element_tag not in element_constructors:
            error_message = f"Unexpected top-level list {list_.tag}!"

            logger.warning(error_message)
            continue

        for element in list_:
            str = etree.tostring(element).decode("utf-8-sig")
            identifiable = element_constructors[element_tag](str)

            if identifiable.id in ret:
                error_message = f"{element} has a duplicate identifier already parsed in the document!"
                raise KeyError(error_message)

            object_store.add(identifiable)
            ret.add(identifiable.id)

    return object_store


def parse_obj_store_to_xml(file: PathOrIO, data: ObjectStore) -> None:
    """
    Serialize a set of AAS objects to an Asset Administration Shell as :class:`~lxml.etree._Element`.

    :param file: A filename or file-like object to read the JSON-serialized data from
    :param data: :class:`ObjectStore <basyx.ObjectStore>` which contains different objects of
                 the AAS meta model which should be serialized to an XML file
    """
    # separate different kind of objects
    asset_administration_shells = []
    submodels = []
    concept_descriptions = []
    for obj in data:
        if isinstance(obj, model.AssetAdministrationShell):
            asset_administration_shells.append(obj)
        elif isinstance(obj, model.Submodel):
            submodels.append(obj)
        elif isinstance(obj, model.ConceptDescription):
            concept_descriptions.append(obj)

    # serialize objects to XML
    root = etree.Element(NS_AAS + "environment", nsmap=XML_NS_MAP)
    if asset_administration_shells:
        et_asset_administration_shells = etree.Element(NS_AAS + "assetAdministrationShells")
        for aas_obj in asset_administration_shells:
            et_asset_administration_shells.append(
                etree.fromstring(aas_xmlization.to_str(aas_obj)))
        root.append(et_asset_administration_shells)
    if submodels:
        et_submodels = etree.Element(NS_AAS + "submodels")
        for sub_obj in submodels:
            et_submodels.append(etree.fromstring(aas_xmlization.to_str(sub_obj)))
        root.append(et_submodels)
    if concept_descriptions:
        et_concept_descriptions = etree.Element(NS_AAS + "conceptDescriptions")
        for con_obj in concept_descriptions:
            et_concept_descriptions.append(etree.fromstring(aas_xmlization.to_str(con_obj)))
        root.append(et_concept_descriptions)
    etree.ElementTree(root).write(file, encoding="UTF-8", xml_declaration=True, method="xml")


class _DetachingTextIOWrapper(io.TextIOWrapper):
    """
    Like :class:`io.TextIOWrapper`, but detaches on context exit instead of closing the wrapped buffer.
    """

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.detach()
