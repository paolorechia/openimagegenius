import Drawer from '@mui/material/Drawer';
import Toolbar from '@mui/material/Toolbar';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import { ListItemButton } from '@mui/material';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Collapse from '@mui/material/Collapse';
import StarBorder from '@mui/icons-material/StarBorder';

const drawerWidth = 300;

export default function RequestsMenu(props) {
    console.log("Requests props", props)
    return (
        <Drawer
            sx={{
                minWidth: drawerWidth,
                flexShrink: 1,
                '& .MuiDrawer-paper': {
                    minWidth: drawerWidth,
                    boxSizing: 'border-box',
                },
            }}
            variant="permanent"
            anchor="right"
        >
            <Toolbar />
            <Divider />
            <Typography variant="h6" noWrap component="div" sx={{ "padding": "30px" }}>
                Your requests
            </Typography>

            <List>
                {
                    props.websockets.state.requests.map(request => {
                        return (
                            <Collapse key={request.data.request_id} in={true} timeout="auto" unmountOnExit>
                                <List component="div" disablePadding>
                                    <ListItem key={request.data.request_id} disablePadding>
                                        <ListItemButton>
                                            <ListItemIcon>
                                                <StarBorder />
                                            </ListItemIcon>
                                            <ListItemText primary={request.data.request_id.substring(0, 5)} />
                                            <ListItemText primary={request.data.prompt} />
                                        </ListItemButton>
                                    </ListItem>
                                </List>
                                {request.data.s3_url ?
                                    <List component="div" disablePadding>
                                        <ListItem key={request.data.s3_url} disablePadding>
                                            <ListItemButton>
                                                <img width="120px" height="120px" src={request.data.s3_url} alt={request.data.prompt} />
                                            </ListItemButton>
                                        </ListItem>
                                    </List>
                                    : ""}
                            </Collapse>
                        )
                    })
                }
            </List>
        </Drawer>
    )
}