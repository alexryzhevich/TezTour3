import React from 'react';
import { connect } from 'react-redux';
import ReactLoading from 'react-loading';
import './Loading.css';

class Loading extends React.PureComponent {
  render() {
    const { isLoading } = this.props;

    return isLoading && (
      <div className="loading-screen">
        <ReactLoading
          type="spinningBubbles"
          className="load-screen-spinning"
          width="100px"
          height="100px"
        />
      </div>
    );
  }
}

const mapStateToProps = state => ({
  isLoading: state.ui.isLoading
});

export default connect(mapStateToProps)(Loading);
