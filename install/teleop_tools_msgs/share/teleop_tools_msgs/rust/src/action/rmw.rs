
#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "teleop_tools_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_Goal() -> *const std::ffi::c_void;
}

#[link(name = "teleop_tools_msgs__rosidl_generator_c")]
extern "C" {
    fn teleop_tools_msgs__action__Increment_Goal__init(msg: *mut Increment_Goal) -> bool;
    fn teleop_tools_msgs__action__Increment_Goal__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Increment_Goal>, size: usize) -> bool;
    fn teleop_tools_msgs__action__Increment_Goal__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Increment_Goal>);
    fn teleop_tools_msgs__action__Increment_Goal__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Increment_Goal>, out_seq: *mut rosidl_runtime_rs::Sequence<Increment_Goal>) -> bool;
}

// Corresponds to teleop_tools_msgs__action__Increment_Goal
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Increment_Goal {

    // This member is not documented.
    #[allow(missing_docs)]
    pub increment_by: rosidl_runtime_rs::Sequence<f32>,

}



impl Default for Increment_Goal {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !teleop_tools_msgs__action__Increment_Goal__init(&mut msg as *mut _) {
        panic!("Call to teleop_tools_msgs__action__Increment_Goal__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Increment_Goal {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_Goal__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_Goal__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_Goal__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Increment_Goal {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Increment_Goal where Self: Sized {
  const TYPE_NAME: &'static str = "teleop_tools_msgs/action/Increment_Goal";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_Goal() }
  }
}


#[link(name = "teleop_tools_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_Result() -> *const std::ffi::c_void;
}

#[link(name = "teleop_tools_msgs__rosidl_generator_c")]
extern "C" {
    fn teleop_tools_msgs__action__Increment_Result__init(msg: *mut Increment_Result) -> bool;
    fn teleop_tools_msgs__action__Increment_Result__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Increment_Result>, size: usize) -> bool;
    fn teleop_tools_msgs__action__Increment_Result__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Increment_Result>);
    fn teleop_tools_msgs__action__Increment_Result__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Increment_Result>, out_seq: *mut rosidl_runtime_rs::Sequence<Increment_Result>) -> bool;
}

// Corresponds to teleop_tools_msgs__action__Increment_Result
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Increment_Result {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for Increment_Result {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !teleop_tools_msgs__action__Increment_Result__init(&mut msg as *mut _) {
        panic!("Call to teleop_tools_msgs__action__Increment_Result__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Increment_Result {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_Result__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_Result__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_Result__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Increment_Result {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Increment_Result where Self: Sized {
  const TYPE_NAME: &'static str = "teleop_tools_msgs/action/Increment_Result";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_Result() }
  }
}


#[link(name = "teleop_tools_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_Feedback() -> *const std::ffi::c_void;
}

#[link(name = "teleop_tools_msgs__rosidl_generator_c")]
extern "C" {
    fn teleop_tools_msgs__action__Increment_Feedback__init(msg: *mut Increment_Feedback) -> bool;
    fn teleop_tools_msgs__action__Increment_Feedback__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Increment_Feedback>, size: usize) -> bool;
    fn teleop_tools_msgs__action__Increment_Feedback__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Increment_Feedback>);
    fn teleop_tools_msgs__action__Increment_Feedback__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Increment_Feedback>, out_seq: *mut rosidl_runtime_rs::Sequence<Increment_Feedback>) -> bool;
}

// Corresponds to teleop_tools_msgs__action__Increment_Feedback
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Increment_Feedback {

    // This member is not documented.
    #[allow(missing_docs)]
    pub structure_needs_at_least_one_member: u8,

}



impl Default for Increment_Feedback {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !teleop_tools_msgs__action__Increment_Feedback__init(&mut msg as *mut _) {
        panic!("Call to teleop_tools_msgs__action__Increment_Feedback__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Increment_Feedback {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_Feedback__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_Feedback__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_Feedback__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Increment_Feedback {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Increment_Feedback where Self: Sized {
  const TYPE_NAME: &'static str = "teleop_tools_msgs/action/Increment_Feedback";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_Feedback() }
  }
}


#[link(name = "teleop_tools_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_FeedbackMessage() -> *const std::ffi::c_void;
}

#[link(name = "teleop_tools_msgs__rosidl_generator_c")]
extern "C" {
    fn teleop_tools_msgs__action__Increment_FeedbackMessage__init(msg: *mut Increment_FeedbackMessage) -> bool;
    fn teleop_tools_msgs__action__Increment_FeedbackMessage__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Increment_FeedbackMessage>, size: usize) -> bool;
    fn teleop_tools_msgs__action__Increment_FeedbackMessage__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Increment_FeedbackMessage>);
    fn teleop_tools_msgs__action__Increment_FeedbackMessage__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Increment_FeedbackMessage>, out_seq: *mut rosidl_runtime_rs::Sequence<Increment_FeedbackMessage>) -> bool;
}

// Corresponds to teleop_tools_msgs__action__Increment_FeedbackMessage
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Increment_FeedbackMessage {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub feedback: super::super::action::rmw::Increment_Feedback,

}



impl Default for Increment_FeedbackMessage {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !teleop_tools_msgs__action__Increment_FeedbackMessage__init(&mut msg as *mut _) {
        panic!("Call to teleop_tools_msgs__action__Increment_FeedbackMessage__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Increment_FeedbackMessage {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_FeedbackMessage__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_FeedbackMessage__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_FeedbackMessage__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Increment_FeedbackMessage {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Increment_FeedbackMessage where Self: Sized {
  const TYPE_NAME: &'static str = "teleop_tools_msgs/action/Increment_FeedbackMessage";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_FeedbackMessage() }
  }
}




#[link(name = "teleop_tools_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_SendGoal_Request() -> *const std::ffi::c_void;
}

#[link(name = "teleop_tools_msgs__rosidl_generator_c")]
extern "C" {
    fn teleop_tools_msgs__action__Increment_SendGoal_Request__init(msg: *mut Increment_SendGoal_Request) -> bool;
    fn teleop_tools_msgs__action__Increment_SendGoal_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Increment_SendGoal_Request>, size: usize) -> bool;
    fn teleop_tools_msgs__action__Increment_SendGoal_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Increment_SendGoal_Request>);
    fn teleop_tools_msgs__action__Increment_SendGoal_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Increment_SendGoal_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<Increment_SendGoal_Request>) -> bool;
}

// Corresponds to teleop_tools_msgs__action__Increment_SendGoal_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Increment_SendGoal_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,


    // This member is not documented.
    #[allow(missing_docs)]
    pub goal: super::super::action::rmw::Increment_Goal,

}



impl Default for Increment_SendGoal_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !teleop_tools_msgs__action__Increment_SendGoal_Request__init(&mut msg as *mut _) {
        panic!("Call to teleop_tools_msgs__action__Increment_SendGoal_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Increment_SendGoal_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_SendGoal_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_SendGoal_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_SendGoal_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Increment_SendGoal_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Increment_SendGoal_Request where Self: Sized {
  const TYPE_NAME: &'static str = "teleop_tools_msgs/action/Increment_SendGoal_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_SendGoal_Request() }
  }
}


#[link(name = "teleop_tools_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_SendGoal_Response() -> *const std::ffi::c_void;
}

#[link(name = "teleop_tools_msgs__rosidl_generator_c")]
extern "C" {
    fn teleop_tools_msgs__action__Increment_SendGoal_Response__init(msg: *mut Increment_SendGoal_Response) -> bool;
    fn teleop_tools_msgs__action__Increment_SendGoal_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Increment_SendGoal_Response>, size: usize) -> bool;
    fn teleop_tools_msgs__action__Increment_SendGoal_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Increment_SendGoal_Response>);
    fn teleop_tools_msgs__action__Increment_SendGoal_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Increment_SendGoal_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<Increment_SendGoal_Response>) -> bool;
}

// Corresponds to teleop_tools_msgs__action__Increment_SendGoal_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Increment_SendGoal_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub accepted: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub stamp: builtin_interfaces::msg::rmw::Time,

}



impl Default for Increment_SendGoal_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !teleop_tools_msgs__action__Increment_SendGoal_Response__init(&mut msg as *mut _) {
        panic!("Call to teleop_tools_msgs__action__Increment_SendGoal_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Increment_SendGoal_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_SendGoal_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_SendGoal_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_SendGoal_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Increment_SendGoal_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Increment_SendGoal_Response where Self: Sized {
  const TYPE_NAME: &'static str = "teleop_tools_msgs/action/Increment_SendGoal_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_SendGoal_Response() }
  }
}


#[link(name = "teleop_tools_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_GetResult_Request() -> *const std::ffi::c_void;
}

#[link(name = "teleop_tools_msgs__rosidl_generator_c")]
extern "C" {
    fn teleop_tools_msgs__action__Increment_GetResult_Request__init(msg: *mut Increment_GetResult_Request) -> bool;
    fn teleop_tools_msgs__action__Increment_GetResult_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Increment_GetResult_Request>, size: usize) -> bool;
    fn teleop_tools_msgs__action__Increment_GetResult_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Increment_GetResult_Request>);
    fn teleop_tools_msgs__action__Increment_GetResult_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Increment_GetResult_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<Increment_GetResult_Request>) -> bool;
}

// Corresponds to teleop_tools_msgs__action__Increment_GetResult_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Increment_GetResult_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub goal_id: unique_identifier_msgs::msg::rmw::UUID,

}



impl Default for Increment_GetResult_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !teleop_tools_msgs__action__Increment_GetResult_Request__init(&mut msg as *mut _) {
        panic!("Call to teleop_tools_msgs__action__Increment_GetResult_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Increment_GetResult_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_GetResult_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_GetResult_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_GetResult_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Increment_GetResult_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Increment_GetResult_Request where Self: Sized {
  const TYPE_NAME: &'static str = "teleop_tools_msgs/action/Increment_GetResult_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_GetResult_Request() }
  }
}


#[link(name = "teleop_tools_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_GetResult_Response() -> *const std::ffi::c_void;
}

#[link(name = "teleop_tools_msgs__rosidl_generator_c")]
extern "C" {
    fn teleop_tools_msgs__action__Increment_GetResult_Response__init(msg: *mut Increment_GetResult_Response) -> bool;
    fn teleop_tools_msgs__action__Increment_GetResult_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Increment_GetResult_Response>, size: usize) -> bool;
    fn teleop_tools_msgs__action__Increment_GetResult_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Increment_GetResult_Response>);
    fn teleop_tools_msgs__action__Increment_GetResult_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Increment_GetResult_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<Increment_GetResult_Response>) -> bool;
}

// Corresponds to teleop_tools_msgs__action__Increment_GetResult_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Increment_GetResult_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub status: i8,


    // This member is not documented.
    #[allow(missing_docs)]
    pub result: super::super::action::rmw::Increment_Result,

}



impl Default for Increment_GetResult_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !teleop_tools_msgs__action__Increment_GetResult_Response__init(&mut msg as *mut _) {
        panic!("Call to teleop_tools_msgs__action__Increment_GetResult_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Increment_GetResult_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_GetResult_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_GetResult_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { teleop_tools_msgs__action__Increment_GetResult_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Increment_GetResult_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Increment_GetResult_Response where Self: Sized {
  const TYPE_NAME: &'static str = "teleop_tools_msgs/action/Increment_GetResult_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__teleop_tools_msgs__action__Increment_GetResult_Response() }
  }
}






#[link(name = "teleop_tools_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__teleop_tools_msgs__action__Increment_SendGoal() -> *const std::ffi::c_void;
}

// Corresponds to teleop_tools_msgs__action__Increment_SendGoal
#[allow(missing_docs, non_camel_case_types)]
pub struct Increment_SendGoal;

impl rosidl_runtime_rs::Service for Increment_SendGoal {
    type Request = Increment_SendGoal_Request;
    type Response = Increment_SendGoal_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__teleop_tools_msgs__action__Increment_SendGoal() }
    }
}




#[link(name = "teleop_tools_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__teleop_tools_msgs__action__Increment_GetResult() -> *const std::ffi::c_void;
}

// Corresponds to teleop_tools_msgs__action__Increment_GetResult
#[allow(missing_docs, non_camel_case_types)]
pub struct Increment_GetResult;

impl rosidl_runtime_rs::Service for Increment_GetResult {
    type Request = Increment_GetResult_Request;
    type Response = Increment_GetResult_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__teleop_tools_msgs__action__Increment_GetResult() }
    }
}


