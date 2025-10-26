import { ThemeProvider } from "./context/themeContext";
import ChatInterface from "./pages/chatInterface";

function App() {
  return (
    <ThemeProvider>
      <ChatInterface />
    </ThemeProvider>
  );
}

export default App;
