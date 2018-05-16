import axios from '../api/axios';
import {
  AUTHORIZATION_HEADER,
  TOKEN_KEY
} from '../constants/constants';
import {
  toggleLoading,
  setError
} from './ui';

const formatTokenHeader = token => `Token ${token}`;

const appendTokenIfPresents = (headers) => {
  const token = localStorage.getItem(TOKEN_KEY);

  return token
    ? {
      ...headers,
      [AUTHORIZATION_HEADER]: formatTokenHeader(token)
    }
    : headers;
};

function beforeRequest(longRequest, dispatch) {
  if (longRequest) {
    dispatch(toggleLoading());
  }
}

function handleResponse(handler, longRequest, dispatch) {
  return (response) => {
    const { data } = response;
    if (handler) {
      handler(data);
    }
    if (longRequest) {
      dispatch(toggleLoading());
    }
  };
}

function handleError(handler, longRequest, dispatch) {
  return (error) => {
    const response = error.response || { status: 500 };
    if (handler) {
      handler(response);
    }
    if (longRequest) {
      dispatch(toggleLoading());
    }
    dispatch(setError(response));
  };
}

export const apiGet = (url, successHandler, errorHandler, headers, longRequest = false) => (dispatch) => {
  beforeRequest(longRequest, dispatch);

  const options = {
    headers: appendTokenIfPresents(headers)
  };
  axios.get(url, options)
    .then(handleResponse(successHandler, longRequest, dispatch))
    .catch(handleError(errorHandler, longRequest, dispatch));
};

export const apiPost = (url, data, successHandler, errorHandler, headers, longRequest = false) => (dispatch) => {
  beforeRequest(longRequest, dispatch);

  const options = {
    headers: appendTokenIfPresents(headers)
  };
  axios.post(url, data, options)
    .then(handleResponse(successHandler, longRequest, dispatch))
    .catch(handleError(errorHandler, longRequest, dispatch));
};

export const apiPut = (url, data, successHandler, errorHandler, headers, longRequest = false) => (dispatch) => {
  beforeRequest(longRequest, dispatch);

  const options = {
    headers: appendTokenIfPresents(headers)
  };
  axios.put(url, data, options)
    .then(handleResponse(successHandler, longRequest, dispatch))
    .catch(handleError(errorHandler, longRequest, dispatch));
};

export const apiDelete = (url, successHandler, errorHandler, headers, longRequest = false) => (dispatch) => {
  beforeRequest(longRequest, dispatch);

  const options = {
    headers: appendTokenIfPresents(headers)
  };
  axios.delete(url, options)
    .then(handleResponse(successHandler, longRequest, dispatch))
    .catch(handleError(errorHandler, longRequest, dispatch));
};
