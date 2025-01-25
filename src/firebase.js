import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
    apiKey: "AIzaSyDGbL9QVBuj4p-xbX8vf7Hg5WBfdNTOkag",
    authDomain: "stok-yonetim-sistemi.firebaseapp.com",
    projectId: "stok-yonetim-sistemi",
    storageBucket: "stok-yonetim-sistemi.appspot.com",
    messagingSenderId: "968770251312",
    appId: "1:968770251312:web:876b5da94f3cc09b3d5bf5"
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);
const storage = getStorage(app);

export { db, storage }; 