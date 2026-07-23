#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "vesc_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vesc_msgs__msg__VescState() -> *const std::ffi::c_void;
}

#[link(name = "vesc_msgs__rosidl_generator_c")]
extern "C" {
    fn vesc_msgs__msg__VescState__init(msg: *mut VescState) -> bool;
    fn vesc_msgs__msg__VescState__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<VescState>, size: usize) -> bool;
    fn vesc_msgs__msg__VescState__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<VescState>);
    fn vesc_msgs__msg__VescState__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<VescState>, out_seq: *mut rosidl_runtime_rs::Sequence<VescState>) -> bool;
}

// Corresponds to vesc_msgs__msg__VescState
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Vedder VESC open source motor controller state (telemetry)

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct VescState {
    /// follow the bledc firwmare: commands.c
    /// fet temperature
    pub temp_fet: f64,

    /// motor temperature
    pub temp_motor: f64,

    /// motor current (ampere) avg_motor_current
    pub current_motor: f64,

    /// input current (ampere) avg_input_current
    pub current_input: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub avg_id: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub avg_iq: f64,

    /// duty cycle (0 to 1) duty_cycle_now
    pub duty_cycle: f64,

    /// motor electrical speed (revolutions per minute) rpm
    pub speed: f64,

    /// input voltage (volt)
    pub voltage_input: f64,

    /// electric charge drawn from input (ampere-hours)
    pub charge_drawn: f64,

    /// electric charge regenerated to input (ampere-hour) amp_hours_charged
    pub charge_regen: f64,

    /// energy drawn from input (watt-hour)
    pub energy_drawn: f64,

    /// energy regenerated to input (watt_hours_charged)
    pub energy_regen: f64,

    /// net tachometer (counts) tachometer
    pub displacement: i32,

    /// total tachnometer (counts) tachometer_abs
    pub distance_traveled: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub fault_code: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pid_pos_now: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub controller_id: i32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub ntc_temp_mos1: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub ntc_temp_mos2: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub ntc_temp_mos3: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub avg_vd: f64,


    // This member is not documented.
    #[allow(missing_docs)]
    pub avg_vq: f64,

}

impl VescState {
    /// fault codes
    pub const FAULT_CODE_NONE: i32 = 0;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const FAULT_CODE_OVER_VOLTAGE: i32 = 1;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const FAULT_CODE_UNDER_VOLTAGE: i32 = 2;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const FAULT_CODE_DRV8302: i32 = 3;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const FAULT_CODE_ABS_OVER_CURRENT: i32 = 4;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const FAULT_CODE_OVER_TEMP_FET: i32 = 5;


    // This constant is not documented.
    #[allow(missing_docs)]
    pub const FAULT_CODE_OVER_TEMP_MOTOR: i32 = 6;

}


impl Default for VescState {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vesc_msgs__msg__VescState__init(&mut msg as *mut _) {
        panic!("Call to vesc_msgs__msg__VescState__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for VescState {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vesc_msgs__msg__VescState__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vesc_msgs__msg__VescState__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vesc_msgs__msg__VescState__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for VescState {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for VescState where Self: Sized {
  const TYPE_NAME: &'static str = "vesc_msgs/msg/VescState";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vesc_msgs__msg__VescState() }
  }
}


#[link(name = "vesc_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vesc_msgs__msg__VescStateStamped() -> *const std::ffi::c_void;
}

#[link(name = "vesc_msgs__rosidl_generator_c")]
extern "C" {
    fn vesc_msgs__msg__VescStateStamped__init(msg: *mut VescStateStamped) -> bool;
    fn vesc_msgs__msg__VescStateStamped__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<VescStateStamped>, size: usize) -> bool;
    fn vesc_msgs__msg__VescStateStamped__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<VescStateStamped>);
    fn vesc_msgs__msg__VescStateStamped__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<VescStateStamped>, out_seq: *mut rosidl_runtime_rs::Sequence<VescStateStamped>) -> bool;
}

// Corresponds to vesc_msgs__msg__VescStateStamped
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Timestamped VESC open source motor controller state (telemetry)

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct VescStateStamped {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub state: super::super::msg::rmw::VescState,

}



impl Default for VescStateStamped {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vesc_msgs__msg__VescStateStamped__init(&mut msg as *mut _) {
        panic!("Call to vesc_msgs__msg__VescStateStamped__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for VescStateStamped {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vesc_msgs__msg__VescStateStamped__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vesc_msgs__msg__VescStateStamped__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vesc_msgs__msg__VescStateStamped__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for VescStateStamped {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for VescStateStamped where Self: Sized {
  const TYPE_NAME: &'static str = "vesc_msgs/msg/VescStateStamped";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vesc_msgs__msg__VescStateStamped() }
  }
}


#[link(name = "vesc_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vesc_msgs__msg__VescImu() -> *const std::ffi::c_void;
}

#[link(name = "vesc_msgs__rosidl_generator_c")]
extern "C" {
    fn vesc_msgs__msg__VescImu__init(msg: *mut VescImu) -> bool;
    fn vesc_msgs__msg__VescImu__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<VescImu>, size: usize) -> bool;
    fn vesc_msgs__msg__VescImu__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<VescImu>);
    fn vesc_msgs__msg__VescImu__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<VescImu>, out_seq: *mut rosidl_runtime_rs::Sequence<VescImu>) -> bool;
}

// Corresponds to vesc_msgs__msg__VescImu
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct VescImu {

    // This member is not documented.
    #[allow(missing_docs)]
    pub ypr: geometry_msgs::msg::rmw::Vector3,


    // This member is not documented.
    #[allow(missing_docs)]
    pub linear_acceleration: geometry_msgs::msg::rmw::Vector3,


    // This member is not documented.
    #[allow(missing_docs)]
    pub angular_velocity: geometry_msgs::msg::rmw::Vector3,


    // This member is not documented.
    #[allow(missing_docs)]
    pub compass: geometry_msgs::msg::rmw::Vector3,


    // This member is not documented.
    #[allow(missing_docs)]
    pub orientation: geometry_msgs::msg::rmw::Quaternion,

}



impl Default for VescImu {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vesc_msgs__msg__VescImu__init(&mut msg as *mut _) {
        panic!("Call to vesc_msgs__msg__VescImu__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for VescImu {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vesc_msgs__msg__VescImu__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vesc_msgs__msg__VescImu__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vesc_msgs__msg__VescImu__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for VescImu {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for VescImu where Self: Sized {
  const TYPE_NAME: &'static str = "vesc_msgs/msg/VescImu";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vesc_msgs__msg__VescImu() }
  }
}


#[link(name = "vesc_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__vesc_msgs__msg__VescImuStamped() -> *const std::ffi::c_void;
}

#[link(name = "vesc_msgs__rosidl_generator_c")]
extern "C" {
    fn vesc_msgs__msg__VescImuStamped__init(msg: *mut VescImuStamped) -> bool;
    fn vesc_msgs__msg__VescImuStamped__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<VescImuStamped>, size: usize) -> bool;
    fn vesc_msgs__msg__VescImuStamped__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<VescImuStamped>);
    fn vesc_msgs__msg__VescImuStamped__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<VescImuStamped>, out_seq: *mut rosidl_runtime_rs::Sequence<VescImuStamped>) -> bool;
}

// Corresponds to vesc_msgs__msg__VescImuStamped
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct VescImuStamped {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub imu: super::super::msg::rmw::VescImu,

}



impl Default for VescImuStamped {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !vesc_msgs__msg__VescImuStamped__init(&mut msg as *mut _) {
        panic!("Call to vesc_msgs__msg__VescImuStamped__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for VescImuStamped {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vesc_msgs__msg__VescImuStamped__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vesc_msgs__msg__VescImuStamped__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { vesc_msgs__msg__VescImuStamped__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for VescImuStamped {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for VescImuStamped where Self: Sized {
  const TYPE_NAME: &'static str = "vesc_msgs/msg/VescImuStamped";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__vesc_msgs__msg__VescImuStamped() }
  }
}


