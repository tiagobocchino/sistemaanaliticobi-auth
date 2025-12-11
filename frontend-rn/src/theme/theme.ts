import { colors } from './colors';

export const theme = {
  colors,
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24,
    xxl: 32,
  },
  radius: {
    sm: 8,
    md: 12,
    lg: 16,
  },
  text: {
    heading: {
      fontSize: 24,
      fontWeight: '700' as const,
      color: colors.white,
    },
    body: {
      fontSize: 16,
      color: colors.text,
    },
  },
};
