#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to vesc_msgs__msg__VescState
/// Vedder VESC open source motor controller state (telemetry)

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::VescState::default())
  }
}

impl rosidl_runtime_rs::Message for VescState {
  type RmwMsg = super::msg::rmw::VescState;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        temp_fet: msg.temp_fet,
        temp_motor: msg.temp_motor,
        current_motor: msg.current_motor,
        current_input: msg.current_input,
        avg_id: msg.avg_id,
        avg_iq: msg.avg_iq,
        duty_cycle: msg.duty_cycle,
        speed: msg.speed,
        voltage_input: msg.voltage_input,
        charge_drawn: msg.charge_drawn,
        charge_regen: msg.charge_regen,
        energy_drawn: msg.energy_drawn,
        energy_regen: msg.energy_regen,
        displacement: msg.displacement,
        distance_traveled: msg.distance_traveled,
        fault_code: msg.fault_code,
        pid_pos_now: msg.pid_pos_now,
        controller_id: msg.controller_id,
        ntc_temp_mos1: msg.ntc_temp_mos1,
        ntc_temp_mos2: msg.ntc_temp_mos2,
        ntc_temp_mos3: msg.ntc_temp_mos3,
        avg_vd: msg.avg_vd,
        avg_vq: msg.avg_vq,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      temp_fet: msg.temp_fet,
      temp_motor: msg.temp_motor,
      current_motor: msg.current_motor,
      current_input: msg.current_input,
      avg_id: msg.avg_id,
      avg_iq: msg.avg_iq,
      duty_cycle: msg.duty_cycle,
      speed: msg.speed,
      voltage_input: msg.voltage_input,
      charge_drawn: msg.charge_drawn,
      charge_regen: msg.charge_regen,
      energy_drawn: msg.energy_drawn,
      energy_regen: msg.energy_regen,
      displacement: msg.displacement,
      distance_traveled: msg.distance_traveled,
      fault_code: msg.fault_code,
      pid_pos_now: msg.pid_pos_now,
      controller_id: msg.controller_id,
      ntc_temp_mos1: msg.ntc_temp_mos1,
      ntc_temp_mos2: msg.ntc_temp_mos2,
      ntc_temp_mos3: msg.ntc_temp_mos3,
      avg_vd: msg.avg_vd,
      avg_vq: msg.avg_vq,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      temp_fet: msg.temp_fet,
      temp_motor: msg.temp_motor,
      current_motor: msg.current_motor,
      current_input: msg.current_input,
      avg_id: msg.avg_id,
      avg_iq: msg.avg_iq,
      duty_cycle: msg.duty_cycle,
      speed: msg.speed,
      voltage_input: msg.voltage_input,
      charge_drawn: msg.charge_drawn,
      charge_regen: msg.charge_regen,
      energy_drawn: msg.energy_drawn,
      energy_regen: msg.energy_regen,
      displacement: msg.displacement,
      distance_traveled: msg.distance_traveled,
      fault_code: msg.fault_code,
      pid_pos_now: msg.pid_pos_now,
      controller_id: msg.controller_id,
      ntc_temp_mos1: msg.ntc_temp_mos1,
      ntc_temp_mos2: msg.ntc_temp_mos2,
      ntc_temp_mos3: msg.ntc_temp_mos3,
      avg_vd: msg.avg_vd,
      avg_vq: msg.avg_vq,
    }
  }
}


// Corresponds to vesc_msgs__msg__VescStateStamped
/// Timestamped VESC open source motor controller state (telemetry)

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct VescStateStamped {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub state: super::msg::VescState,

}



impl Default for VescStateStamped {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::VescStateStamped::default())
  }
}

impl rosidl_runtime_rs::Message for VescStateStamped {
  type RmwMsg = super::msg::rmw::VescStateStamped;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        state: super::msg::VescState::into_rmw_message(std::borrow::Cow::Owned(msg.state)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        state: super::msg::VescState::into_rmw_message(std::borrow::Cow::Borrowed(&msg.state)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      state: super::msg::VescState::from_rmw_message(msg.state),
    }
  }
}


// Corresponds to vesc_msgs__msg__VescImu

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct VescImu {

    // This member is not documented.
    #[allow(missing_docs)]
    pub ypr: geometry_msgs::msg::Vector3,


    // This member is not documented.
    #[allow(missing_docs)]
    pub linear_acceleration: geometry_msgs::msg::Vector3,


    // This member is not documented.
    #[allow(missing_docs)]
    pub angular_velocity: geometry_msgs::msg::Vector3,


    // This member is not documented.
    #[allow(missing_docs)]
    pub compass: geometry_msgs::msg::Vector3,


    // This member is not documented.
    #[allow(missing_docs)]
    pub orientation: geometry_msgs::msg::Quaternion,

}



impl Default for VescImu {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::VescImu::default())
  }
}

impl rosidl_runtime_rs::Message for VescImu {
  type RmwMsg = super::msg::rmw::VescImu;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        ypr: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(msg.ypr)).into_owned(),
        linear_acceleration: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(msg.linear_acceleration)).into_owned(),
        angular_velocity: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(msg.angular_velocity)).into_owned(),
        compass: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(msg.compass)).into_owned(),
        orientation: geometry_msgs::msg::Quaternion::into_rmw_message(std::borrow::Cow::Owned(msg.orientation)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        ypr: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(&msg.ypr)).into_owned(),
        linear_acceleration: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(&msg.linear_acceleration)).into_owned(),
        angular_velocity: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(&msg.angular_velocity)).into_owned(),
        compass: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(&msg.compass)).into_owned(),
        orientation: geometry_msgs::msg::Quaternion::into_rmw_message(std::borrow::Cow::Borrowed(&msg.orientation)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      ypr: geometry_msgs::msg::Vector3::from_rmw_message(msg.ypr),
      linear_acceleration: geometry_msgs::msg::Vector3::from_rmw_message(msg.linear_acceleration),
      angular_velocity: geometry_msgs::msg::Vector3::from_rmw_message(msg.angular_velocity),
      compass: geometry_msgs::msg::Vector3::from_rmw_message(msg.compass),
      orientation: geometry_msgs::msg::Quaternion::from_rmw_message(msg.orientation),
    }
  }
}


// Corresponds to vesc_msgs__msg__VescImuStamped

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct VescImuStamped {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub imu: super::msg::VescImu,

}



impl Default for VescImuStamped {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::VescImuStamped::default())
  }
}

impl rosidl_runtime_rs::Message for VescImuStamped {
  type RmwMsg = super::msg::rmw::VescImuStamped;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        imu: super::msg::VescImu::into_rmw_message(std::borrow::Cow::Owned(msg.imu)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        imu: super::msg::VescImu::into_rmw_message(std::borrow::Cow::Borrowed(&msg.imu)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      imu: super::msg::VescImu::from_rmw_message(msg.imu),
    }
  }
}


