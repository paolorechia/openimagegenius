import React, { useState } from 'react';
import Box from '@mui/material/Box';
import CssBaseline from '@mui/material/CssBaseline';
import Toolbar from '@mui/material/Toolbar';

import Header from './Components/Header';
import SideMenu from './Components/SideMenu';
import NotificationMenu from './Components/NotificationMenu';
import ImageDetailScreen from './Screens/ImageDetailScreen';
import PromptScreen from './Screens/PromptScreen';

const drawerWidth = 240;


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
          selectedScreen == "prompt"
            ? <PromptScreen />
            : <ImageDetailScreen />
        }
      </Box>
      <NotificationMenu />
    </Box>
  );
}

export default App;