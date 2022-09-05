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
  const [isDrawerOpen, setIsDrawerOpen] = useState(true)
  const [isRequestsDrawerOpen, setIsRequestsDrawerOpen] = useState(true)


  const websockets = {
    manager: WebsocketManager,
    state: websocketState,
    setState: setWebsocketState
  }

  function handleDrawerOpen() {
    setIsDrawerOpen(true)
  }

  function handleDrawerClose() {
    setIsDrawerOpen(false)
  }

  function handleRequestDrawerOpen() {
    setIsRequestsDrawerOpen(true)
  }

  function handleRequestDrawerClose() {
    setIsRequestsDrawerOpen(false)
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
    <Box sx={{ display: 'flex', width: "100%"}}>
      <CssBaseline />
      <Header
        handleDrawerOpen={handleDrawerOpen}
        isDrawerOpen={isDrawerOpen}
        handleRequestDrawerOpen={handleRequestDrawerOpen}
        isRequestsDrawerOpen={isRequestsDrawerOpen}
      />
      <SideMenu
        selectedScreen={selectedScreen}
        setScreenCallback={setScreen}
        handleDrawerClose={handleDrawerClose}
        isDrawerOpen={isDrawerOpen}
      />
      <Box
        component="main"
        sx={{ flexGrow: 1, bgcolor: 'background.default', p: 3 }}
      >
        <Toolbar />
        {
          !websockets.state.connected ?
            <CircularProgress />
            : websockets.state.authorized ?
              selectedScreen === "prompt"
                ? <PromptScreen websockets={websockets} />
                : <ImageDetailScreen websockets={websockets} />
              : <Unauthorized />
        }
        <RequestsMenu
          websockets={websockets}
          isRequestsDrawerOpen={isRequestsDrawerOpen}
          handleRequestDrawerClose={handleRequestDrawerClose}
        />

      </Box>
    </Box>
  );
}

export default App;