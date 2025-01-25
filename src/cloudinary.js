import { Cloudinary } from 'cloudinary-core';

const cloudinaryConfig = {
  cloud_name: 'dyq45xbl7',
  api_key: '616531696468618',
  api_secret: 'WvEjNrXSn_S4_GDHdr3InWa057w',
  upload_preset: 'urun_resimleri'
};

export const cloudinary = new Cloudinary({
  cloud_name: cloudinaryConfig.cloud_name,
  secure: true
});

export const uploadPreset = cloudinaryConfig.upload_preset; 