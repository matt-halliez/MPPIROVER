cmake_minimum_required(VERSION 3.5)
project(f1tenth_intersection_driver)

find_package(ament_cmake REQUIRED)

# Install launch and config directories
install(DIRECTORY
  launch
  config
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
