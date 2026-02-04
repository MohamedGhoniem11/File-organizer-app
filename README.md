# FileManager Pro

FileManager Pro is a production-grade Python application designed for automated file organization and real-time directory monitoring. Built with a modular, service-oriented architecture, it provides a robust engine for classifying and managing files while offering a modern graphical interface for administrative control.

## Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Configuration](#configuration)
- [Directory Health and Cleanup](#directory-health-and-cleanup)
- [Development and Testing](#development-and-testing)
- [Deployment](#deployment)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## Features
- **Real-time Monitoring**: Integrated `watchdog` service for instantaneous processing of incoming files.
- **Intelligent Classification**: Custom mapping of file extensions to logical categories via JSON configuration.
- **Health and Housekeeping**: Automated discovery of empty directories, duplicate files (via SHA-256 hashing), and orphaned files.
- **Safety-First Deletion**: Mandatory dry-run mode for cleanup operations with GUI-based confirmation prompts.
- **Modern UI**: Streamlined dashboard built with `customtkinter` featuring real-time status and logs.
- **Configuration Management**: Persistent JSON-based configuration with live hot-reloading support.
- **Standalone Packaging**: Pre-configured build scripts for Windows executable distribution.

## Architecture
The project adheres to a strict separation of concerns to facilitate extensibility:

- **`src/core/`**: Implementation of business logic, including classification engines, file system organizers, and health auditing tools.
- **`src/gui/`**: Presentation layer containing individual view components (Dashboard, Logs, Settings, Maintenance) and the main application container.
- **`src/services/`**: Infrastructure layer providing singletons for configuration management, logging, and background observation.
- **`src/utils/`**: Shared utility functions for path sanitization and string processing.

## Getting Started

### Prerequisites
- Python 3.10 or higher.

### Installation
1. Clone the repository to your local machine.
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### GUI Mode
Launch the primary application dashboard:
```bash
python -m src.main
```

### Operational Modes
- **Monitoring**: Background service that watches the configured `Downloads` folder.
- **Maintenance**: Manual or scheduled auditing of directory health to reclaim storage and remove redundancy.

## Configuration
Application settings are managed via `config/config.json`. Key parameters include:

- `watch_directory`: Absolute path to the directory under monitoring.
- `categories`: Mapping of category identifiers to lists of supported file extensions.
- `monitor_enabled`: Boolean flag to control background observation.
- `collision_strategy`: Strategy for handling filename conflicts (`rename`, `skip`, or `overwrite`).
- `cleanup`: Parameters for auditing, including `dry_run` and `handle_orphans` policies.

## Directory Health and Cleanup
The Health Engine provides comprehensive auditing capabilities:
- **Deduplication**: Identification of identical file contents using SHA-256 hashing, regardless of filename.
- **Orphan Management**: Handling of files that do not match defined classification rules (defaults to `move_to_misc`).
- **Safety Protocols**: All destructive operations require explicit user consent and default to non-destructive simulation (Dry-Run).

## Development and Testing

### Testing
Verify project integrity using `pytest`:
```bash
pytest
```
The test suite utilizes mocks to ensure no actual file system mutations occur during validation.

### CI/CD
Automated testing is integrated into the development workflow via GitHub Actions, as defined in `.github/workflows/tests.yml`.

## Deployment
To bundle the application into a standalone Windows executable, execute the provided batch script:
```bash
build_exe.bat
```
The resulting binary will be generated in the `dist/` directory.

## Roadmap
- **NLP Integration**: Natural language search capabilities for semantic file retrieval.
- **Cloud Integration**: Support for Dropbox and Google Drive synchronization.
- **Network Support**: Monitoring and organization for network-mapped drives.

## Contributing
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/NewFeature`).
3. Commit your changes (`git commit -m 'Add NewFeature'`).
4. Push to the branch (`git push origin feature/NewFeature`).
5. Open a Pull Request.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
