import {
  TOGGLE_LOADING,
  SET_ERROR
} from '../constants/actions/ui';

export const toggleLoading = () => ({
  type: TOGGLE_LOADING
});

export const setError = payload => ({
  type: SET_ERROR,
  payload
});
