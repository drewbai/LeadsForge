import { render, screen } from "@testing-library/react";

import App from "../src/App";

test("renders app heading", () => {
  render(<App />);

  expect(screen.getByText("LeadsForge Frontend OK")).toBeInTheDocument();
});
