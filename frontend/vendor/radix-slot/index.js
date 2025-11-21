const React = require("react");

const Slot = React.forwardRef(function Slot(props, forwardedRef) {
  const { children, ...slotProps } = props;

  if (React.isValidElement(children)) {
    const mergedProps = {
      ...slotProps,
      ...children.props,
      className: [slotProps.className, children.props.className]
        .filter(Boolean)
        .join(" ") || undefined,
      style: { ...(slotProps.style || {}), ...(children.props.style || {}) },
      ref: forwardedRef ?? children.ref,
    };

    return React.cloneElement(children, mergedProps);
  }

  return React.createElement(React.Fragment, null, children);
});

module.exports = { Slot };
