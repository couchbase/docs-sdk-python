setup() {
	load 'node_modules/bats-support/load'
	load 'node_modules/bats-assert/load'

	HOWTOS_DIR=../modules/howtos/examples
	PROJECT_DOCS_DIR=../modules/project-docs/examples
	HELLO_WORLD_DIR=../modules/hello-world/examples

	BATS_TEST_RETRIES=3
}

function runExample() {
	cd $1
	run python $2
}

diag() {
	printf ' # %s\n' "$@" >&3
}
