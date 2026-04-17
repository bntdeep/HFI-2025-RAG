import { Router } from 'express';
import multer from 'multer';
import FormData from 'form-data';
import { pythonClient } from '../python/client.js';

const router = Router();
const upload = multer({ storage: multer.memoryStorage() });

router.get('/', async (_req, res, next) => {
  try {
    res.json(await pythonClient.listDocuments());
  } catch (err) {
    next(err);
  }
});

router.post('/', upload.single('file'), async (req, res, next) => {
  try {
    if (!req.file) {
      res.status(422).json({ error: 'No file uploaded' });
      return;
    }
    const form = new FormData();
    form.append('file', req.file.buffer, {
      filename: req.file.originalname,
      contentType: req.file.mimetype,
    });
    res.json(await pythonClient.uploadDocument(form));
  } catch (err) {
    next(err);
  }
});

router.delete('/:id', async (req, res, next) => {
  try {
    res.json(await pythonClient.deleteDocument(req.params.id));
  } catch (err) {
    next(err);
  }
});

export default router;
