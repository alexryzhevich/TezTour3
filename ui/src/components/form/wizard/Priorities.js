import React from 'react';
import range from 'lodash/range';
import { Label, FormGroup, Col } from 'reactstrap';
import { Field } from 'redux-form';
import { DAYS } from '../../../constants/constants';

import renderPrioritiesInput from '../utils/renderPrioritiesInput';

class Priorities extends React.Component {
  constructor(props) {
    super(props);

    this.initialize = this.initialize.bind(this);
  }

  componentDidMount() {
    const { minDays, maxDays } = this.props;
    this.initialize(minDays, maxDays);
  }

  initialize(minDays, maxDays) {
    const { fields } = this.props;
    const count = (Number(maxDays) - Number(minDays)) + 1;

    fields.removeAll();
    range(0, count).forEach(() => fields.push(null));
  }

  render() {
    const { fields, minDays } = this.props;

    const priorities = fields.map((item, index) => {
      const dayNumber = Number(minDays) + index;
      const label = `${dayNumber} ${DAYS}`;
      return (
        <FormGroup key={index} row>
          <Col sm={4} />
          <Label
            for="name"
            sm={2}
          >
            { label }
          </Label>
          <Col sm={3}>
            <Field
              name={`priorities[${index}]`}
              type="text"
              component={renderPrioritiesInput}
              typeValue="%"
            />
          </Col>
        </FormGroup>
      );
    });

    return (
      <div>
        { priorities }
      </div>
    );
  }
}

export default Priorities;
