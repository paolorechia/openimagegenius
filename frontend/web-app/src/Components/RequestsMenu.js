import Box from '@mui/material/Box';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import { ListItemButton } from '@mui/material';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Collapse from '@mui/material/Collapse';
import StarBorder from '@mui/icons-material/StarBorder';
import { Stack } from '@mui/system';
import Drawer from '@mui/material/Drawer';
import ChrevonRightIcon from '@mui/icons-material/ChevronRight';
import { IconButton } from '@mui/material';

const drawerWidth = 150;

export default function RequestsMenu(props) {
    console.log("Requests props", props)
    return (
        <Drawer
            open={props.isRequestsDrawerOpen}
            sx={{
                minWidth: drawerWidth,
                maxWidth: drawerWidth * 2,
                flexShrink: 1,
                '& .MuiDrawer-paper': {
                    minWidth: drawerWidth * 2,
                    boxSizing: 'border-box',
                },
            }}
            variant="persistent"
            anchor="right"
        >
            <Box sx={{
                "display": "flex",
                "justifyContent": "left",
                "padding": "11.4px"
            }}>
                <IconButton onClick={props.handleRequestDrawerClose}>
                    <ChrevonRightIcon
                        sx={{ "marginTop": "0px", "marginBottom": "0px", "marginRight": "0px" }}
                    />
                </IconButton>
            </Box>
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
                                            <Stack>
                                                <ListItemText primary={request.data.request_id.substring(0, 5)} />
                                                <ListItemText
                                                    primary={request.data.prompt}
                                                    primaryTypographyProps={{
                                                        variant: 'subtitle2',
                                                        style: {
                                                            overflow: 'hidden',
                                                            textOverflow: 'ellipsis'
                                                        }
                                                    }}
                                                />
                                            </Stack>
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