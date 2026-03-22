import { Stack } from 'expo-router';

export default function RootLayout() {
  return (
    <Stack>
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="new" options={{ title: 'Nouvelle transaction', presentation: 'modal' }} />
    </Stack>
  );
}
