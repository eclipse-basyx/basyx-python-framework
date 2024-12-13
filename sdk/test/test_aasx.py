# Copyright (c) 2022 the Eclipse BaSyx Authors
#
# This program and the accompanying materials are made available under the terms of the MIT License, available in
# the LICENSE file of this project.
#
# SPDX-License-Identifier: MIT
import datetime
import hashlib
import io
import os
import tempfile
import unittest
import warnings
from pathlib import Path  # Used for easier handling of auxiliary file's local path

import pyecma376_2
from aas_core3 import types as model
from basyx import aasx

from . import example_aas
from basyx.object_store import ObjectStore

from .example_aas import create_full_example


class TestAASXUtils(unittest.TestCase):
    def test_supplementary_file_container(self) -> None:
        container = aasx.DictSupplementaryFileContainer()
        with open(Path(__file__).parent.parent / 'basyx' / 'tutorial' /
                  'data' / 'TestFile.pdf', 'rb') as f:
            new_name = container.add_file("/TestFile.pdf", f, "application/pdf")
            # Name should not be modified, since there is no conflict
            self.assertEqual("/TestFile.pdf", new_name)
            f.seek(0)
            container.add_file("/TestFile.pdf", f, "application/pdf")
        # Name should not be modified, since there is still no conflict
        self.assertEqual("/TestFile.pdf", new_name)

        with open(__file__, 'rb') as f:
            new_name = container.add_file("/TestFile.pdf", f, "application/pdf")
        # Now, we have a conflict
        self.assertNotEqual("/TestFile.pdf", new_name)
        self.assertIn(new_name, container)

        # Check metadata
        self.assertEqual("application/pdf", container.get_content_type("/TestFile.pdf"))
        self.assertEqual("b18229b24a4ee92c6c2b6bc6a8018563b17472f1150d35d5a5945afeb447ed44",
                         container.get_sha256("/TestFile.pdf").hex())
        self.assertIn("/TestFile.pdf", container)

        # Check contents
        file_content = io.BytesIO()
        container.write_file("/TestFile.pdf", file_content)
        self.assertEqual(hashlib.sha1(file_content.getvalue()).hexdigest(), "78450a66f59d74c073bf6858db340090ea72a8b1")

        # Add same file again with different content_type to test reference counting
        with open(__file__, 'rb') as f:
            duplicate_file = container.add_file("/TestFile.pdf", f, "image/jpeg")
        self.assertIn(duplicate_file, container)

        # Delete files
        container.delete_file(new_name)
        self.assertNotIn(new_name, container)
        # File should still be accessible
        container.write_file(duplicate_file, file_content)

        container.delete_file(duplicate_file)
        self.assertNotIn(duplicate_file, container)
        # File should now not be accessible anymore
        with self.assertRaises(KeyError):
            container.write_file(duplicate_file, file_content)


class AASXWriterTest(unittest.TestCase):
    def test_writing_reading_example_aas(self) -> None:
        # Create example data and file_store
        data = example_aas.create_full_example()
        files = aasx.DictSupplementaryFileContainer()
        with open(Path(__file__).parent.parent / 'basyx' /
                  'tutorial' / 'data' / 'TestFile.pdf', 'rb') as f:
            files.add_file("/aasx/suppl/MyExampleFile.pdf", f, "application/pdf")
            f.seek(0)

        # Create OPC/AASX core properties
        cp = pyecma376_2.OPCCoreProperties()
        cp.created = datetime.datetime.now()
        cp.creator = "Eclipse BaSyx Python Testing Framework"

        # Write AASX file
        for write_json in (False, True):
            with self.subTest(write_json=write_json):
                fd, filename = tempfile.mkstemp(suffix="test.aasx")
                os.close(fd)

                # Write AASX file
                # the zipfile library reports errors as UserWarnings via the warnings library. Let's check for
                # warnings
                with warnings.catch_warnings(record=True) as w:
                    with aasx.AASXWriter(filename) as writer:
                        # TODO test writing multiple AAS
                        writer.write_aas(['https://acplt.org/Test_AssetAdministrationShell'],
                                         data, files, write_json=write_json)
                        writer.write_core_properties(cp)

                assert isinstance(w, list)  # This should be True due to the record=True parameter
                self.assertEqual(0, len(w), f"Warnings were issued while writing the AASX file: "
                                            f"{[warning.message for warning in w]}")

                # Read AASX file
                new_data: ObjectStore[model.Identifiable] = ObjectStore()
                new_files = aasx.DictSupplementaryFileContainer()
                with aasx.AASXReader(filename) as reader:
                    reader.read_into(new_data, new_files)
                    new_cp = reader.get_core_properties()

                # Check core properties
                assert isinstance(cp.created, datetime.datetime)  # to make mypy happy
                self.assertIsInstance(new_cp.created, datetime.datetime)
                assert isinstance(new_cp.created, datetime.datetime)  # to make mypy happy
                self.assertAlmostEqual(new_cp.created, cp.created, delta=datetime.timedelta(milliseconds=20))
                self.assertEqual(new_cp.creator, "Eclipse BaSyx Python Testing Framework")
                self.assertIsNone(new_cp.lastModifiedBy)

                # Check files
                self.assertEqual(new_files.get_content_type("/aasx/suppl/MyExampleFile.pdf"), "application/pdf")
                file_content = io.BytesIO()
                new_files.write_file("/aasx/suppl/MyExampleFile.pdf", file_content)
                self.assertEqual(hashlib.sha1(file_content.getvalue()).hexdigest(),
                                 "78450a66f59d74c073bf6858db340090ea72a8b1")

                # Override read objects
                with aasx.AASXReader(filename) as reader:
                    reader.read_into(new_data, new_files, replace_existing=True)
                    new_cp = reader.get_core_properties()

                # Reload objects while expected to skipp all
                with self.assertLogs(level='INFO') as log:
                    with aasx.AASXReader(filename) as reader:
                        reader.read_into(new_data, new_files)
                        new_cp = reader.get_core_properties()
                    assert isinstance(log.output, list)  # This should be True due to the record=True parameter
                    self.assertEqual(len(log.output), 2)

                os.unlink(filename)

        # Test AASXReader exceptions
        new_data_2: ObjectStore[model.Identifiable] = ObjectStore()
        new_files = aasx.DictSupplementaryFileContainer()
        with self.assertRaises(FileNotFoundError):
            with aasx.AASXReader("/Non_existing_dir") as reader:
                reader.read_into(new_data_2, new_files)
        with self.assertRaises(Exception):
            with open(Path(__file__).parent / "./__init__.py") as f:
                with aasx.AASXReader(f) as reader:
                    pass
