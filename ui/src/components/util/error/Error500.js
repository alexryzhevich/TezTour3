import React from 'react';
import {
  OOPS_LABEL,
  SMTH_BAD_HAPPEND_LABEL
} from '../../../constants/constants';

const ErrorPage = () => (
  <div className="error-page">
    <h1>{OOPS_LABEL}</h1>
    <h2>{SMTH_BAD_HAPPEND_LABEL}</h2>
  </div>
);

export default ErrorPage;
