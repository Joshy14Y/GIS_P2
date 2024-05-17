import { configureStore } from '@reduxjs/toolkit'
import idReducer from './idSlice.js';

const store = configureStore({
    reducer: {
        identifier: idReducer,
    },
})

export default store