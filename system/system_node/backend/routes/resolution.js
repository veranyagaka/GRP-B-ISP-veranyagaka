import express from "express";
import multer from "multer";
import { resolveImage } from "../controllers/resolutionController.js";

const router = express.Router();
const upload = multer({
  dest: path.join(__dirname, '../public/uploads')
});

router.post("/resolve", upload.single("image"), resolveImage);

export default router;
