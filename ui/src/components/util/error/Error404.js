import React from 'react';
import {
  PAGE_NOT_FOUND_LABEL,
  HMM_LABEL
} from '../../../constants/constants';

const ErrorPage = () => (
  <div className="error-page">
    <h1>{HMM_LABEL}</h1>
    <h2>{PAGE_NOT_FOUND_LABEL}</h2>
  </div>
);

export default ErrorPage;
