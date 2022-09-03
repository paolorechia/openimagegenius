import Drawer from '@mui/material/Drawer';
import Toolbar from '@mui/material/Toolbar';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';

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
                            <ListItem key={request.data.request_id} disablePadding>
                                {request.data.request_id}
                            </ListItem>
                        )
                    })
                }
            </List>
        </Drawer>
    )
}