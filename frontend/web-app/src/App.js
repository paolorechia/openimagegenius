import React, { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';
import { Alert, CircularProgress } from '@mui/material';

import Header from './Components/Header';
import SideMenu from './Components/SideMenu';
import RequestsMenu from './Components/RequestsMenu';
import ImageDetailScreen from './Screens/ImageDetailScreen';
import PromptScreen from './Screens/PromptScreen';
import WebsocketManager from './Components/WebsocketManager';
import Unauthorized from './Components/Unauthorized';
import Snackbar from '@mui/material/Snackbar';

function App() {
  const [selectedScreen, setScreen] = useState("prompt")
  const [isWebsocketReady, setIsWebsocketReady] = useState(false)
  const [websocketState, setWebsocketState] = useState({
    "connected": false,
    "authorized": false,
    "busy": false,
    "requests": [],
  })
  const [notifications, setNotifications] = useState([])
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

  function handleSnackBarClose() {
    setNotifications([])
  }
  useEffect(() => {
    if (!isWebsocketReady) {
      setTimeout(function () {
        setIsWebsocketReady(true)
      }, 500)
    } else {
      if (!websocketState.authorized && !websocketState.connected) {
        WebsocketManager.setStateCallback(websocketState, setWebsocketState, setNotifications)
        WebsocketManager.start_connection()
      }
    }
    if (websocketState.busy) {
      setTimeout(function () {
        setWebsocketState({ ...websocketState, busy: false })
      }, 2000)
    }
    console.log("State change", websocketState)
  }, [isWebsocketReady, websocketState, notifications]);
  return (
    <Box sx={{ display: 'flex', width: "100%" }}>
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
      {notifications.map((notification, index) => {
        return (
          <Box>
            <Snackbar
              anchorOrigin={{ "vertical": "bottom", "horizontal": "center" }}
              key={index}
              open={true}
              autoHideDuration={6000}
              onClose={handleSnackBarClose}
            >
              {
                notification.data === "authorized"
                  ? <Alert severity='info' onClose={handleSnackBarClose}>Authorization successful!</Alert>
                  : notification.data === "unauthorized"
                    ? <Alert severity='error' onClose={handleSnackBarClose}>Authorization failed!</Alert>
                    : notification.message_type === "request_accepted"
                      ? <Alert severity="success" onClose={handleSnackBarClose}>Your request has been accepted.</Alert>
                      : notification.message_type === "job_complete"
                        ? <Alert severity="success" onClose={handleSnackBarClose}>A job has completed!</Alert>
                        :
                        notification.message_type === "job_failed"
                          ? <Alert severity="error" onClose={handleSnackBarClose}>A job has failed!</Alert>
                          : <Alert severity="error" onClose={handleSnackBarClose}>An error has occurred: {notification.data}</Alert>
              }
            </Snackbar>
          </Box>
        )
      })}
    </Box>
  );
}

export default App;