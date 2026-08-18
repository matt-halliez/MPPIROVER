# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_f1tenth_mppi_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED f1tenth_mppi_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(f1tenth_mppi_FOUND FALSE)
  elseif(NOT f1tenth_mppi_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(f1tenth_mppi_FOUND FALSE)
  endif()
  return()
endif()
set(_f1tenth_mppi_CONFIG_INCLUDED TRUE)

# output package information
if(NOT f1tenth_mppi_FIND_QUIETLY)
  message(STATUS "Found f1tenth_mppi: 0.0.0 (${f1tenth_mppi_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'f1tenth_mppi' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${f1tenth_mppi_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(f1tenth_mppi_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${f1tenth_mppi_DIR}/${_extra}")
endforeach()
