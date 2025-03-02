import { initializeApp } from "firebase/app"; 
import { getAuth } from "firebase/auth"; 
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

const firebaseConfig = {
    apiKey: "**our api key**",
    authDomain: "**our projectID.firebaseapp.com**", 
    projectId: "**our project id**",
    storageBucket: "**our projectID.appspot.com",
    messagingSenderId: "**our messaging sender id", 
    appId: "**our app id**"
};

const app = initializeApp(firebaseConfig); 
export const auth = getAuth(app); 
export const db = getFirestore(app); 
export const storage = getStorage(app); 