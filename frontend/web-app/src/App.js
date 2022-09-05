import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import { CircularProgress } from '@mui/material';

import Header from './Components/Header';
import SideMenu from './Components/SideMenu';
import RequestsMenu from './Components/RequestsMenu';
import ImageDetailScreen from './Screens/ImageDetailScreen';
import PromptScreen from './Screens/PromptScreen';
import WebsocketManager from './Components/WebsocketManager';
import Unauthorized from './Components/Unauthorized';

function App() {
  const [selectedScreen, setScreen] = useState("prompt")
  const [isWebsocketReady, setIsWebsocketReady] = useState(false)
  const [websocketState, setWebsocketState] = useState({
    "connected": false,
    "authorized": false,
    "requests": [],
  })

  const websockets = {
    manager: WebsocketManager,
    state: websocketState,
    setState: setWebsocketState
  }

  useEffect(() => {
    if (!isWebsocketReady) {
      setTimeout(function () {
        setIsWebsocketReady(true)
      }, 500)
    } else {
      if (!websocketState.authorized && !websocketState.connected) {
        WebsocketManager.setStateCallback(websocketState, setWebsocketState)
        WebsocketManager.start_connection()
      }
    }
    console.log("State change", websocketState)
  }, [isWebsocketReady, websocketState]);

  return (
    <Box sx={{ display: 'flex', minWidth: "300px" }}>
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
          !websockets.state.connected ?
          <CircularProgress />
          :  websockets.state.authorized ? 
              selectedScreen === "prompt"
                ? <PromptScreen websockets={websockets} />
                : <ImageDetailScreen websockets={websockets} />
              : <Unauthorized />  
        }
      </Box>
      <RequestsMenu websockets={websockets} />
    </Box>
  );
}

export default App;