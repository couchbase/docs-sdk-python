load 'test_helper'

@test "[hello-world] - hello_world_t.py" {
  runExample $HELLO_WORLD_DIR hello_world_t.py
  assert_success
}