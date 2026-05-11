import { Navigate, Route, Routes } from "react-router-dom";

import AppLayout from "./layouts/AppLayout";
import LeadsLayout from "./layouts/LeadsLayout";
import AboutPage from "./pages/AboutPage";
import HomePage from "./pages/HomePage";
import PlaceholderPage from "./pages/PlaceholderPage";
import LeadsDetailPage from "./pages/leads/LeadsDetailPage";
import LeadsListPage from "./pages/leads/LeadsListPage";
import LeadsNewPage from "./pages/leads/LeadsNewPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<HomePage />} />
        <Route
          path="metrics"
          element={
            <PlaceholderPage title="Metrics" phase={5} description="Metrics dashboard (UI Phase 5)." />
          }
        />
        <Route
          path="subscriptions"
          element={
            <PlaceholderPage
              title="Subscriptions"
              phase={6}
              description="Subscription management (UI Phase 6)."
            />
          }
        />
        <Route
          path="settings"
          element={
            <PlaceholderPage title="Settings" phase={7} description="Settings and admin (UI Phase 7)." />
          }
        />
        <Route path="about" element={<AboutPage />} />
        <Route element={<LeadsLayout />}>
          <Route path="leads" element={<LeadsListPage />} />
          <Route path="leads/new" element={<LeadsNewPage />} />
          <Route path="leads/:leadId" element={<LeadsDetailPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
