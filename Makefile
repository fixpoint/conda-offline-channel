LANG     := C
CYAN     := \033[36m
GREEN    := \033[32m
RESET    := \033[0m
CONDA    := conda
ANACONDA := anaconda


# http://postd.cc/auto-documented-makefile/
.DEFAULT_GOAL := help
.PHONY: help
help: ## Show this help
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "${CYAN}%-30s${RESET} %s\n", $$1, $$2}'

.PHONY: build
build: ## Build packages for each Python
	@echo "${GREEN}Building packages for each Python${RESET}"
	@rm -rf .conda-bld
	@${CONDA} build ${ARGS} --python 2.7 --output-folder .conda-bld --override-channels --channel defaults --channel conda-forge .
	@${CONDA} build ${ARGS} --python 3.4 --output-folder .conda-bld --override-channels --channel defaults --channel conda-forge .
	@${CONDA} build ${ARGS} --python 3.5 --output-folder .conda-bld --override-channels --channel defaults --channel conda-forge .
	@${CONDA} build ${ARGS} --python 3.6 --output-folder .conda-bld --override-channels --channel defaults --channel conda-forge .
	@${CONDA} build ${ARGS} --python 3.7 --output-folder .conda-bld --override-channels --channel defaults --channel conda-forge .


.PHONY: convert
convert: ## Convert each packages for all platforms
	@echo "${GREEN}Convert each packages for all platforms${RESET}"
	@${CONDA} convert ${ARGS} -f --platform all  .conda-bld/*/conda-offline-channel-*.tar.bz2 -o .conda-bld


.PHONY: upload
upload: ## Upload all packages
	@echo "${GREEN}Upload all packages${RESET}"
	@${ANACONDA} upload --force .conda-bld/linux-32/conda-offline-channel-*.tar.bz2
	@${ANACONDA} upload --force .conda-bld/linux-64/conda-offline-channel-*.tar.bz2
	@${ANACONDA} upload --force .conda-bld/osx-64/conda-offline-channel-*.tar.bz2
	@${ANACONDA} upload --force .conda-bld/win-32/conda-offline-channel-*.tar.bz2
	@${ANACONDA} upload --force .conda-bld/win-64/conda-offline-channel-*.tar.bz2
