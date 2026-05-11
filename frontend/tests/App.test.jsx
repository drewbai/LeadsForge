import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import App from "../src/App";

test("renders app heading", () => {
  render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  );

  expect(screen.getByRole("heading", { name: "LeadsForge" })).toBeInTheDocument();
});
