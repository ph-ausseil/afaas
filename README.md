# My Personal AutoGPT Extension for Memory Enhancement

Welcome to the **My Personal AutoGPT Extension for Memory Enhancement** project! This repository is a personal effort aimed at enhancing the AutoGPT framework with memory back-end integration and segregation of agent provisioning logic and agent processing logic.

## Project Overview

This repository contains three main branches, each serving a specific purpose:

1. **[core-memory-ext-integration (stable*)](https://github.com/ph-ausseil/Auto-GPT/tree/core-memory-ext-integration)**: This branch hosts a library designed to facilitate the integration of various NoSQL backends into the AutoGPT framework. The library aims to provide seamless management of different NoSQL storage solutions, making it easier to store and retrieve data efficiently. This branch is considered stable and suitable for use.

2. **[core-memory-ext-integration (unstable)](https://github.com/ph-ausseil/Auto-GPT/tree/core-memory-ext-integration)**: This branch represents a copy of the AutoGPT core package with memory extension integrated. The idea is to outline that we could manage memory differently.

3. **[memory-ext-and-loop-integration (stable*)](https://github.com/ph-ausseil/Auto-GPT/tree/memory-ext-and-loop-integration)**: This branch mirrors the AutoGPT core package but with integrated memory extension. Additionally, it segregates the agent provisioning logic and agent processing logic. This configuration aims to achieve a stable integration of memory enhancements while maintaining clear separation of logic components.

## Supported backends

As of today JSONFileMemory is the only supported backend. You would have to modify `default_agent_settings.yml` with these lines : 

```yaml
memory:
storage_format: installed_package
storage_route: autogpt.core.memory.nosql.jsonfile.JSONFileMemory
```

## Contributing

Contributions to this project are welcomed and encouraged. You can participate by:

- Testing and providing feedback on the stable branch for supported memory back-ends.
- Test or Implement prototyped backends (DynamoDB, CosmosDB & MongoDB backends).
- Offering suggestions, reporting issues, or proposing enhancements through GitHub issues.

For more information read CONTRIBUTING.md

## Install & execute 

1 - Install autogpt.core as per the [procedure](https://github.com/Significant-Gravitas/Auto-GPT/blob/master/autogpt/core/README.md)
2 - Modify `default_agent_settings.yml` as explained in `Supported backends` 
3 - Execute `autogpt/core/runner/cli_app/cli.py run`,

## License

The code in this repository is currently governed by a temporary contributor license, as outlined in the [LICENSE](LICENSE) file. Please refer to the license for usage details and limitations. The project acknowledges the use of code derived from AutoGPT, which is licensed under the MIT License. The terms and conditions of the MIT License can be found in the [THIRD_PARTY_NOTICES.txt](THIRD_PARTY_NOTICES.txt) file.

## Contact

For questions, feedback, or inquiries about this project, feel free to reach out to the project owner, Pierre-Henri AUSSEIL, at [ph.ausseil@gmail.com](mailto:ph.ausseil@gmail.com).
