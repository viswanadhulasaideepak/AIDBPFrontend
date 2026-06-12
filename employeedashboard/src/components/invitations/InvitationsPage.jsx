import React, { useState } from "react";
import InvitationsTab from "./InvitationsTab";
import MembersTab from "../members/MembersTab";
import ReactivationsTab from "../reactivations/ReactivationsTab";
import DashboardLayout from "../layout/DashboardLayout";
import "./InvitationsPage.css"

function InvitationsPage() {
  const [activeSection, setActiveSection] = useState("invitations");

  return (
    <div>
      <DashboardLayout >
      <h1>Invitations Module</h1>
      <nav>
        <button onClick={() => setActiveSection("invitations")}>Invitations</button>
        <button onClick={() => setActiveSection("members")}>Members</button>
        <button onClick={() => setActiveSection("reactivation")}>Reactivation Requests</button>
      </nav>

      {activeSection === "invitations" && <InvitationsTab />}
      {activeSection === "members" && <MembersTab />}
      {activeSection === "reactivation" && <ReactivationsTab />}
      </DashboardLayout>
    </div>
  );
}

export default InvitationsPage;
