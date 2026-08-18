# generated from rosidl_cmake/cmake/rosidl_cmake_aggregate_target-extras.cmake.in

# Create a convenience aggregate target vesc_msgs::vesc_msgs
# that links all generated interface targets, so downstream packages can use
# a single modern CMake target name instead of ${vesc_msgs_TARGETS}.
if(vesc_msgs_TARGETS AND NOT TARGET vesc_msgs::vesc_msgs)
  add_library(vesc_msgs::vesc_msgs INTERFACE IMPORTED)
  set_target_properties(vesc_msgs::vesc_msgs PROPERTIES
    INTERFACE_LINK_LIBRARIES "${vesc_msgs_TARGETS}")
endif()
