import { Box, CssBaseline } from "@mui/material";
import PrimaryAppBar from "./temp/PrimaryAppBar";
import PrimaryDraw from "./temp/PrimaryDraw";
const Home = () => {
  return (
    <Box sx={{ display: "flex" }}>
      <CssBaseline />
      <PrimaryAppBar />
      <PrimaryDraw></PrimaryDraw>
    </Box>
  );
};
export default Home;
