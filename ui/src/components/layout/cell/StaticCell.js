import React from 'react';
import classnames from 'classnames';

class StaticCell extends React.PureComponent {
  render() {
    const { value, diagonal, required } = this.props;

    const className = classnames({
      'precomputed-td': !required,
      'diagonal-td': diagonal
    });

    return (
      <div className={className}>
        {value}
      </div>
    );
  }
}

export default StaticCell;
