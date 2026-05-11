import { Outlet } from "react-router-dom";

import { LocalLeadsProvider } from "../context/LocalLeadsContext";

export default function LeadsLayout() {
  return (
    <LocalLeadsProvider>
      <Outlet />
    </LocalLeadsProvider>
  );
}
