import { Outlet } from "react-router-dom";

import { LeadsProvider } from "../context/LeadsContext";

export default function LeadsLayout() {
  return (
    <LeadsProvider>
      <Outlet />
    </LeadsProvider>
  );
}
