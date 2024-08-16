# Eclipse BaSyx Python Framework

> [!warning]
> This project is heavily Work in Progress!

The Eclipse BaSyx Python Framework is the successor of the [Eclipse BaSyx SDK](https://github.com/eclipse-basyx/basyx-python-sdk) and is based on generated code from [aas-core-works](https://github.com/aas-core-works/).

## Repository Structure
We follow a monolithic repository structure, with several Python projects inside this repository. 
The idea behind this is that you can pick and choose, which Python packages you need for your specific use case and do not get one very bloated package with a whole AAS server, when all you want is to write AAS files.
Here's the available Python projects:

- [SDK](./sdk/README.md): AAS object handling
- WIP Server: AAS API and server implementation
- WIP Client: AAS API Client
- WIP Compliance Tool: AAS Compliance Checker

