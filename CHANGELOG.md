# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.3] - 2020-04-19
### Added
- Tests for overriding VPC defaults and specifying new VPCs.

### Changed
- Continue parsing the configuration files when the default VPC config details are not available.
- Test fixtures are now split into cluster and fargate container directories.

## [0.0.2] - 2020-04-16
### Added
- An example cluster.yml config file
- Additional documentation around usage and configuration
- A TODO list

### Changed
- ClusterStack and SharedPrivateALB classes to use the new application_port config

## [0.0.1] - 2020-04-15
### Added
- CDK modules for deploying a Shared ECS Cluster + ALB + Fargate Containers.
