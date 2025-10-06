import React, { useState } from 'react';
import { motion } from 'framer-motion';
import './AnimatedButton.css';

const AnimatedButton = ({ children, onClick }) => {
  const [isHovered, setHovered] = useState(false);
  const [isClicked, setClicked] = useState(false);

  const handleClick = () => {
    setClicked(true);
    onClick && onClick();
    setTimeout(() => setClicked(false), 300);
  };

  return (
    <motion.button
      className="animated-button"
      onHoverStart={() => setHovered(true)}
      onHoverEnd={() => setHovered(false)}
      onClick={handleClick}
      whileHover={{ scale: 1.1, boxShadow: '0px 4px 15px rgba(0,0,0,0.2)' }}
      animate={{
        scale: isClicked ? 0.95 : 1,
        boxShadow: isClicked ? '0px 0px 8px rgba(255, 0, 150, 0.7)' : '',
      }}
      transition={{
        type: 'spring',
        stiffness: 300,
        damping: 20,
      }}
      aria-label="Animated interactive button"
    >
      {children}
      <motion.span
        className="ripple"
        animate={{
          opacity: isClicked ? [1, 0] : 0,
          scale: isClicked ? [0, 2] : 0,
        }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      />
    </motion.button>
  );
};

export default AnimatedButton;
