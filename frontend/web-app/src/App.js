import React, { useState } from 'react';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';

import Header from './Components/Header';
import SideMenu from './Components/SideMenu';
import NotificationMenu from './Components/NotificationMenu';
import ImageDetailScreen from './Screens/ImageDetailScreen';
import PromptScreen from './Screens/PromptScreen';
import WebsocketManager from './Components/WebsocketManager';

let websocket = null;
if (websocket === null) {
  websocket = WebsocketManager()
  console.log(websocket)
}
websocket.addEventListener("error", (error) => {
  console.error(error)
})
websocket.addEventListener("close", (event) => {
  console.log("Close event", event)
})

websocket.addEventListener("message", (event) => {
  console.log("Received message ", event)
  if (event.data === "authorized") {
    websocket.send(
      JSON.stringify(
        {
          "action": "request",
          "request_type": "prompt",
          "data": "A cowboy cat"
        }
      )
    )
  }
})
websocket.addEventListener('open', (event) => {
  console.log("Opened", event)
  websocket.send(
    JSON.stringify(
      {
        "action": "authorize",
        "token": "89480825643960485537603252629543680"
      }
    )
  )
})

function App() {
  const [selectedScreen, setScreen] = useState("prompt")

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <Header />
      <SideMenu
        selectedScreen={selectedScreen}
        setScreenCallback={setScreen}
      />
      <Box
        component="main"
        sx={{ flexGrow: 1, bgcolor: 'background.default', p: 3 }}
      >
        <Toolbar />
        {
          selectedScreen === "prompt"
            ? <PromptScreen />
            : <ImageDetailScreen />
        }
      </Box>
      <NotificationMenu />
    </Box>
  );
}

export default App;