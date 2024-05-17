import { createSlice } from '@reduxjs/toolkit';

export const idSlice = createSlice({
  name: 'identifier',
  initialState: {
    id: null, // Estado inicial para el ID
  },
  reducers: {
    addId: (state, action) => {
      state.id = action.payload; // Agrega el ID al estado
    },
    removeId: (state) => {
      state.id = null; // Elimina el ID del estado
    },
  },
});

// Action creators are generated for each case reducer function
export const { addId, removeId } = idSlice.actions;

export default idSlice.reducer;
