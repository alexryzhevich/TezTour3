import React from 'react';
import sum from 'lodash/sum';
import './Priorities.css';
import { CURRENT_SUM_EQUAL_TO_LABEL } from '../../../constants/constants';

const PrioritiesDescription = ({ priorities, description }) => {
  const prioritiesInt = priorities ? priorities.map(item => Number(item)) : [];
  const currentSumPercent = sum(prioritiesInt);
  return (
    <div className="info-priority-message">
      <div>
        {description}
      </div>
      <div>
        {CURRENT_SUM_EQUAL_TO_LABEL} {currentSumPercent}%
      </div>
    </div>
  );
};

export default PrioritiesDescription;
