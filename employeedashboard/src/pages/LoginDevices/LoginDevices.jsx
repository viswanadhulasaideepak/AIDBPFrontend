import React, { useEffect, useState } from "react";
import toast from "react-hot-toast";
import DashboardLayout from "../../components/layout/DashboardLayout";
import {fetchMyLoginDevices,renameTrustedDevice,removeTrustedDevice,
  logoutDevice,logoutAllDevices,trustDevice} from "../../services/api";
import "./LoginDevices.css";

const LoginDevices = () => {
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadDevices = async () => {
    try {
      setLoading(true);
      const data = await fetchMyLoginDevices();
      setDevices(data);
    } catch (err) {
      toast.error("Failed to load devices.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDevices();
  }, []);

const handleTrust = async (device) => {
  try {
    await trustDevice(device.id);
    toast.success("Device marked as trusted");
    loadDevices();
  } catch {
    toast.error("Unable to trust device");
  }
};  

  const handleRename = async (device) => {
    const name = prompt(
      "Enter new device name",
      device.device_name
    );

    if (!name) return;

    try {
      await renameTrustedDevice(device.id, name);
      toast.success("Device renamed");
      loadDevices();
    } catch {
      toast.error("Rename failed");
    }
  };

  const handleRemove = async (device) => {
    if (!window.confirm("Remove trusted device?")) return;

    try {
      await removeTrustedDevice(device.id);
      toast.success("Trusted device removed");
      loadDevices();
    } catch {
      toast.error("Unable to remove device");
    }
  };

  const handleLogout = async (device) => {
    if (!window.confirm("Logout this device?")) return;

    try {
      await logoutDevice(device.id);
      toast.success("Logged out");
      loadDevices();
    } catch {
      toast.error("Logout failed");
    }
  };

  const handleLogoutAll = async () => {
    if (!window.confirm("Logout all other devices?")) return;

    try {
      await logoutAllDevices();
      toast.success("Other sessions logged out");
      loadDevices();
    } catch {
      toast.error("Operation failed");
    }
  };

  return (
    <DashboardLayout>
      <div className="login-devices-page">
        <div className="login-devices-header">
          <h2>Login Devices</h2>
          <button className="logout-all-btn" onClick={handleLogoutAll}>
            Logout All Other Devices
          </button>
        </div>

        {loading ? (
          <p>Loading...</p>
        ) : (

          <table className="devices-table">
            <thead>
              <tr>
                <th>Device</th>
                <th>Browser</th>
                <th>IP Address</th>
                <th>Login Time</th>
                <th>Last Activity</th>
                <th>Status</th>
                <th>Trusted</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>

              {devices.map((device) => (

                <tr key={device.id}>
                  <td>{device.device_name}</td>
                  <td>{device.browser}</td>
                  <td>{device.ip_address}</td>
                  <td>
                    {new Date(device.login_time).toLocaleString()}
                  </td>

                  <td>
                    {new Date(device.last_activity).toLocaleString()}
                  </td>

                  <td>
                    <span className={`status ${device.status}`}>
                     {device.status}
                    </span>
                  </td>

                 <td>
                  {device.is_trusted ? "Yes" : "No"}
                </td>
                <td>
                  {!device.is_trusted && (
                    <button onClick={() => handleTrust(device)}>
                      Trust
                    </button>
                  )}

                  {device.is_trusted && (
                    <>
                   {device.is_trusted && (
                    <button onClick={() => handleRename(device)}>
                      Rename
                    </button>
                  )}

                    <button onClick={() => handleRemove(device)}>
                      Remove Trusted
                    </button>
                    </>
                  )}

              {device.status === "active" && (
                <button onClick={() => handleLogout(device)}>
                  Logout
                </button>
              )}
              </td>
              </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </DashboardLayout>
  );
};

export default LoginDevices;