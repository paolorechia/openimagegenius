import Drawer from '@mui/material/Drawer';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ChatBubbleOutlineTwoToneIcon from '@mui/icons-material/ChatBubbleOutlineTwoTone';
import Divider from '@mui/material/Divider';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import { Box } from '@mui/system';
import { IconButton } from '@mui/material';
import ImageTwoToneIcon from '@mui/icons-material/ImageTwoTone'

const drawerWidth = 240;

export default function SideMenu(props) {
    function setPromptScreen() {
        props.setScreenCallback("prompt")
    }

    function setGalleryScreen() {
        props.setScreenCallback("gallery")
    }

    return (
        <Drawer
            open={props.isDrawerOpen}
            sx={{
                width: drawerWidth,
                flexShrink: 0,
                '& .MuiDrawer-paper': {
                    width: drawerWidth,
                    boxSizing: 'border-box',
                },
            }}
            variant="persistent"
            anchor="left"
        >
            <Box sx={{
                "display": "flex",
                "justifyContent": "right",
                "padding": "11.4px"
            }}>
                <IconButton onClick={props.handleDrawerClose}>
                    <ChevronLeftIcon
                        sx={{ "marginTop": "0px", "marginBottom": "0px", "marginRight": "0px" }}
                    />
                </IconButton>
            </Box>
            <Divider />
            <List>
                <ListItem key="Prompt" disablePadding onClick={setPromptScreen}>
                    <ListItemButton>
                        <ListItemIcon>
                            <ChatBubbleOutlineTwoToneIcon />
                        </ListItemIcon>
                        {props.selectedScreen === "prompt"
                            ? <ListItemText secondary="Prompt" />
                            : <ListItemText primary="Prompt" />
                        }
                    </ListItemButton>
                </ListItem>
                <ListItem key="Gallery" disablePadding onClick={setGalleryScreen}>
                    <ListItemButton>
                        <ListItemIcon>
                            <ImageTwoToneIcon />
                        </ListItemIcon>
                        {props.selectedScreen === "gallery"
                            ? <ListItemText secondary="Gallery" />
                            : <ListItemText primary="Gallery" />
                        }
                    </ListItemButton>
                </ListItem>
            </List>
        </Drawer>
    )
}