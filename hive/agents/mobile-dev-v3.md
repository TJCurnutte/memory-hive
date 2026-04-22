# React Native vs Flutter, Mobile Architecture, Offline-First, Push Notifications — v3

> Production mobile development reference. Updated 2026.

---

## 1. React Native vs Flutter — Decision Framework 2025/2026

### Architecture Overview

**React Native (New Architecture: Fabric + TurboModules)**:
- Bridge-based communication replaced by JSI (JavaScript Interface)
- TurboModules: native module loading without bridge serialization
- Fabric: new rendering system, synchronous UI updates
- New Architecture is default as of RN 0.76+ (2024)
- Hermes JS engine: optimized for mobile, ahead-of-time compilation
- Third-party libraries: massive ecosystem, but quality varies; bridge dependencies can be painful

**Flutter (Skia → Impeller rendering)**:
- Impeller (default since Flutter 3.16): precompiled shaders, eliminates shader compilation jank
- Dart compiles to native ARM via AOT compilation
- Widget system: fully custom (not native UIKit/Android Views)
- FFI for Rust/C/C++ library binding
- No bridge — direct platform channels via MethodChannel/EventChannel
- 120fps target on high refresh rate displays

### When to Choose Each

| Factor | React Native | Flutter |
|---|---|---|
| Team JS/TS expertise | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Existing React codebases | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Native UI integration (complex) | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Performance-critical animations | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Quick prototyping | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Long-term maintenance | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Third-party library availability | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Hot reload during development | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Custom platform channels | Manual | First-class |
| Memory footprint | ~20-30MB | ~15MB |

**Decision heuristics:**
- "Our team knows React" → RN
- "We need pixel-perfect custom animations" → Flutter
- "We need the best native UI look-and-feel" → RN
- "We need complex cross-platform native modules" → RN (native modules ecosystem deeper)
- "We're building from scratch, team is flexible" → evaluate project complexity + team skills
- "We need a single codebase for web+mobile+desktop" → RN with React Native Web or RN + Electron/Tauri

---

## 2. Mobile Architecture Patterns

### Clean Architecture (Both Platforms)

```
┌─────────────────────────────────────┐
│         Presentation Layer          │
│   (Screens, Widgets, ViewModels)   │
├─────────────────────────────────────┤
│          Domain Layer               │
│  (Use Cases, Entities, Interfaces) │
├─────────────────────────────────────┤
│           Data Layer                │
│  (Repositories, Data Sources, DTO) │
└─────────────────────────────────────┘
```

### Feature-Based Modular Architecture

```
src/
├── features/
│   ├── auth/
│   │   ├── domain/           # Entities, use cases
│   │   ├── data/             # API, local DB, repository impl
│   │   └── presentation/     # Screens, BLoC, widgets
│   ├── feed/
│   │   └── ...
│   └── settings/
│       └── ...
├── core/
│   ├── di/                   # Dependency injection
│   ├── network/              # HTTP client
│   ├── routing/             # Navigation
│   └── utils/
└── app/
    └── App.tsx / main.dart
```

**Benefits**: Feature modules can be developed independently, lazy-loaded, and shared across apps. Critical for large teams.

### Navigation

**Flutter — GoRouter**:
```dart
// go_router setup
final router = GoRouter(
  initialLocation: '/splash',
  routes: [
    GoRoute(
      path: '/feed',
      builder: (context, state) => FeedScreen(
        tag: state.uri.queryParameters['tag'],
      ),
      redirect: (context, state) {
        if (!authState.isAuthenticated) return '/login';
        return null;
      },
    ),
  ],
  errorBuilder: (context, state) => ErrorScreen(state.error),
);
```

**React Native v6 — React Navigation**:
```tsx
// React Navigation v6
const RootStack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

<NavigationContainer>
  <RootStack.Navigator>
    <RootStack.Screen name="Main" component={MainTabs} />
    <RootStack.Screen name="Detail" component={DetailScreen}
      options={{ presentation: 'modal', animation: 'slide_from_bottom' }}
    />
  </RootStack.Navigator>
</NavigationContainer>

// Deep linking
const linking = {
  prefixes: ['myapp://'],
  config: { screens: { Main: { screens: { Feed: 'feed/:tag' } } } }
};
```

---

## 3. State Management Deep Dive

### Flutter: BLoC vs Riverpod vs GetX

**BLoC** (Business Logic Component) — most enterprise adoption:
```dart
// bloc/feed_bloc.dart
class FeedBloc extends Bloc<FeedEvent, FeedState> {
  final FeedRepository repository;

  FeedBloc({required this.repository}) : super(FeedInitial()) {
    on<LoadFeed>(_onLoadFeed);
    on<RefreshFeed>(_onRefreshFeed);
  }

  Future<void> _onLoadFeed(LoadFeed event, Emitter<FeedState> emit) async {
    emit(FeedLoading());
    try {
      final posts = await repository.getFeed();
      emit(FeedLoaded(posts: posts));
    } catch (e) {
      emit(FeedError(message: e.toString()));
    }
  }
}

// usage in widget
BlocBuilder<FeedBloc, FeedState>(
  builder: (context, state) {
    return switch (state) {
      FeedInitial() => SizedBox(),
      FeedLoading() => CircularProgressIndicator(),
      FeedLoaded(:final posts) => ListView.builder(
          itemCount: posts.length,
          itemBuilder: (_, i) => PostCard(posts[i]),
        ),
      FeedError(:final message) => ErrorWidget(message),
    };
  },
)
```

**Riverpod** — compile-safe, testable, no build_runner needed:
```dart
// With Riverpod 2.0
@riverpod
Future<List<Post>> feed(Ref ref) async {
  return ref.read(repositoryProvider).getFeed();
}

// Consumer
ref.watch(feedProvider).when(
  data: (posts) => ListView(...),
  loading: () => Loader(),
  error: (e, _) => Error(e),
)
```

**Comparison**:

| Criteria | BLoC | Riverpod | GetX |
|---|---|---|---|
| Boilerplate | High | Low | Very Low |
| Testability | Excellent | Excellent | Moderate |
| Type safety | Full | Full | Partial |
| Learning curve | Moderate | Low | Low |
| Reactive streams | Streams | AsyncValue | Rx observables |
| Best for | Enterprise | Modern apps | Rapid dev |

### React Native: Zustand vs Redux Toolkit vs Jotai

**Zustand** — minimal, middleware support, no boilerplate:
```tsx
// store/useAuthStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthState {
  user: User | null;
  token: string | null;
  login: (credentials: Credentials) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      login: async (creds) => {
        const { user, token } = await authApi.login(creds);
        set({ user, token });
      },
      logout: () => set({ user: null, token: null }),
    }),
    { name: 'auth-storage' }
  )
);

// Usage
const { user, login } = useAuthStore();
```

**TanStack Query (React Query)** — for server state:
```tsx
// Server state management (cache + sync)
const { data: posts, isLoading, refetch } = useQuery({
  queryKey: ['feed', 'global'],
  queryFn: () => api.getFeed(),
  staleTime: 60 * 1000,       // 1 min before refetch
  gcTime: 10 * 60 * 1000,      // 10 min garbage collection
  refetchOnWindowFocus: true,
  retry: 2,
});

// Mutations with optimistic updates
const createPost = useMutation({
  mutationFn: (newPost) => api.createPost(newPost),
  onMutate: async (newPost) => {
    await queryClient.cancelQueries({ queryKey: ['feed'] });
    const previous = queryClient.getQueryData(['feed']);
    queryClient.setQueryData(['feed'], (old) => [newPost, ...old]);
    return { previous };
  },
  onError: (_, __, context) => {
    queryClient.setQueryData(['feed'], context.previous);
  },
  onSettled: () => queryClient.invalidateQueries(['feed']),
});
```

### Local Persistence

**Flutter**: Hive (fast, lightweight NoSQL), Isar (SQLite with reactive queries):
```dart
// Hive setup
import 'package:hive_flutter/hive_flutter.dart';

await Hive.initFlutter();
await Hive.openBox<User>('users');
var userBox = Hive.box<User>('users');
await userBox.put('current', User(name: 'Travis', email: 'travis@example.com'));
final user = userBox.get('current');
```

**React Native**: MMKV (fast key-value), AsyncStorage (simple), WatermelonDB (relational):
```tsx
import { MMKV } from 'react-native-mmkv';
const storage = new MMKV({ id: 'app-storage' });
storage.set('user', JSON.stringify(user));
const user = JSON.parse(storage.getString('user') ?? '{}');
```

---

## 4. Offline-First Architecture

### CRDT-Based Sync

CRDTs (Conflict-free Replicated Data Types): data structures that can be updated independently and merged without conflicts.

**Key CRDT types:**
- G-Set (Grow-only Set): can only add elements, never remove
- OR-Set (Observed-Remove Set): add/remove with tombstones
- LWW-Register: Last-Writer-Wins register
- CRDT-Table: mergeable tabular data

**Implementation: Automerge (JS/Dart)**:
```typescript
import Automerge from '@automerge/automerge';

const doc = Automerge.init();
const newDoc = Automerge.change(doc, (d) => {
  d.posts = [{ id: '1', title: 'Hello', body: '...' }];
});

// Sync between peers
const [binary, patch] = Automerge.save(doc);
const newDoc = Automerge.load(binary);

// Two peers editing independently
const [doc1, patch1] = Automerge.applyChanges(doc, changes);
const [doc2, patch2] = Automerge.applyChanges(doc, otherChanges);
```

### WatermelonDB (React Native)

```typescript
import { Database } from '@nozbe/watermelondb';
import SQLiteAdapter from '@nozbe/watermelondb/adapters/sqlite';

const adapter = new SQLiteAdapter({
  schema,
  dbName: 'app',
  jsi: true,       // JS-C++ bindings, fast
  onSetUpError: (error) => console.error(error),
});

const database = new Database({ adapter });

// Define model
class Post extends Model {
  static table = 'posts';
  @text('title') title!: string;
  @field('is_completed') isCompleted!: boolean;
  @date('created_at') createdAt!: Date;
  @children('comments') comments!: Query<Comment>;
}

// Reactive queries — automatically update when DB changes
const posts = database.get<Post>('posts').query(
  Q.where('is_completed', false),
  Q.sortBy('created_at', Q.desc),
).observe();

// Optimistic write: update UI immediately, sync in background
async function togglePost(post: Post) {
  await database.write(async () => {
    await post.update((p) => { p.isCompleted = !p.isCompleted; });
  });
  syncQueue.enqueue({ type: 'UPDATE_POST', payload: post.id });
}
```

### Drift (Flutter — SQLite ORM)

```dart
// drift database setup
import 'package:drift/drift.dart';
import 'package:drift/native.dart';

LazyDatabase _openConnection() {
  return LazyDatabase(() => NativeDatabase.file(File('db.sqlite')));
}

@DriftDatabase(tables: [Posts, Comments])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 1;

  // Reactive stream queries
  Stream<List<Post>> watchAllPosts() =>
    (select(posts)..orderBy([(t) => OrderingTerm.desc(t.createdAt)])).watch();

  // Complex queries
  Future<List<Post>> postsWithComments() async {
    return (select(posts).join([
      leftOuterJoin(comments, comments.postId.equalsExp(posts.id)),
    ])).get();
  }
}
```

### Conflict Resolution Strategies

| Strategy | Use Case | Implementation |
|---|---|---|
| LWW (Last-Write-Wins) | Simple, most cases | Timestamp comparison |
| Operational Transform | Text editing | CRDT-based (Automerge) |
| 3-way merge | Structured data | Version tracking + merge |
| Server-wins | Authoritative data | Always accept server version |
| Manual resolution | Critical conflicts | Flag for user resolution |

**Background sync queue**:
```typescript
class SyncQueue {
  private queue: SyncOperation[] = [];
  private isProcessing = false;

  enqueue(op: SyncOperation) {
    this.queue.push(op);
    this.process();
  }

  async process() {
    if (this.isProcessing) return;
    this.isProcessing = true;

    while (this.queue.length > 0) {
      const op = this.queue.shift()!;
      try {
        await this.syncService.sync(op);
      } catch (e) {
        // Retry with exponential backoff
        await this.delay(Math.pow(2, op.retryCount) * 1000);
        op.retryCount++;
        if (op.retryCount < 5) this.queue.unshift(op);
        else this.queueFailed(op); // Alert user
      }
    }

    this.isProcessing = false;
  }
}
```

### Network Reachability

```dart
// Flutter
import 'package:connectivity_plus/connectivity_plus.dart';

StreamSubscription<List<ConnectivityResult>> subscription =
  Connectivity().onConnectivityChanged.listen((results) {
    if (results.contains(ConnectivityResult.none)) {
      // Offline: show offline banner, enable offline mode
    }
  });
```

```tsx
// React Native
import NetInfo from '@react-native-community/netinfo';

useEffect(() => {
  const unsubscribe = NetInfo.addEventListener((state) => {
    if (!state.isConnected) setOfflineMode(true);
    else if (offlineMode) syncAndReconnect();
  });
  return unsubscribe;
}, []);
```

---

## 5. Push Notifications

### Architecture Overview

```
Your Server → FCM/APNs → Device → App (foreground/background)
```

### Firebase Cloud Messaging (FCM) Setup

```dart
// Flutter: firebase_messaging setup
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationService {
  final _messaging = FirebaseMessaging.instance;
  final _local = FlutterLocalNotificationsPlugin();

  Future<void> initialize() async {
    // Request permission
    NotificationSettings settings = await _messaging.requestPermission(
      alert: true, badge: true, sound: true, provisional: false,
    );

    // iOS: get APNs token
    final apnsToken = await _messaging.getAPNSToken();

    // Handle foreground messages
    FirebaseMessaging.onMessage.listen(_showLocalNotification);

    // Handle background/terminated taps
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);
  }

  Future<void> _showLocalNotification(RemoteMessage message) async {
    const android = AndroidInitializationSettings('@mipmap/ic_launcher');
    const ios = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );
    const init = InitializationSettings(android: android, iOS: ios);
    await _local.initialize(init);

    await _local.show(
      message.notification.hashCode,
      message.notification?.title,
      message.notification?.body,
      NotificationDetails(
        android: AndroidNotificationDetails(
          'high_priority', 'High Priority',
          channelDescription: 'Critical notifications',
          importance: Importance.max,
          priority: Priority.high,
          styleInformation: BigTextStyleInformation(message.notification!.body!),
        ),
        iOS: const DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        ),
      ),
    );
  }
}
```

### React Native: notifee (best cross-platform)

```tsx
// React Native notifee
import notifee, { AndroidImportance, EventType } from '@notifee/react-native';

async function setupNotifications() {
  // Request permission
  await notifee.requestPermission();

  // Create channel (Android)
  await notifee.createChannel({
    id: 'urgent',
    name: 'Urgent Updates',
    importance: AndroidImportance.HIGH,
    sound: 'urgent_alert',
    vibration: true,
  });

  // Foreground listener
  notifee.displayNotification({
    title: 'New Message',
    body: 'You have a new message from Travis',
    ios: { sound: 'default' },
    android: {
      channelId: 'urgent',
      pressAction: { id: 'default' },
      smallIcon: 'ic_notification',
    },
  });

  // Background event listener
  notifee.onBackgroundEvent(async ({ type, detail }) => {
    if (type === EventType.ACTION_PRESS && detail.pressAction?.id === 'reply') {
      // Handle quick reply from notification
    }
  });
}
```

### Rich Notification Payloads

```dart
// Image notification (iOS + Android)
final bigPicture = BigPictureStyleInformation(
  DrawableResourceAndroidBitmap('hero_image'),
  contentTitle: 'Breaking News',
  summaryText: '3 min read',
);

await _local.show(
  0, 'Breaking News', 'Story headline here',
  NotificationDetails(
    android: AndroidNotificationDetails('news', 'News', styleInformation: bigPicture),
    iOS: DarwinNotificationDetails(
      attachments: [IOSNotificationAttachment.fromUrl('https://.../image.jpg')],
    ),
  ),
);

// Actionable notifications (iOS)
const actions = [
  { title: 'Reply', foreground: true, pressAction: { id: 'reply' } },
  { title: 'Archive', pressAction: { id: 'archive' } },
  { title: 'Mark Read', pressAction: { id: 'mark_read' } },
];
```

### Android 13+ Runtime Permission (Critical)

```dart
// Android 13+ requires runtime permission check
Future<bool> checkNotificationPermission() async {
  if (Platform.isAndroid) {
    // Android 13+ uses POST_NOTIFICATIONS permission
    final androidInfo = await DeviceInfoPlugin().androidInfo;
    if (androidInfo.version.sdkInt >= 33) {
      final result = await _messaging.requestPermission();
      return result.authorizationStatus == AuthorizationStatus.authorized;
    }
  }
  return true; // Older Android: no runtime permission needed
}

// Show rationale dialog before requesting
Future<void> showPermissionRationale() async {
  // In your UI, explain WHY notifications are needed
  // Then call requestPermission()
}
```

### iOS Notification Service Extension (for media attachments)

```swift
// NotificationServiceExtension.swift
// Add this target in Xcode to intercept notifications before display
// Required for: large images, decryption, modifying content
class NotificationService: UNNotificationServiceExtension {
    var contentHandler: ((UNNotificationContent) -> Void)?
    var bestAttemptContent: UNNotificationContent?

    override func didReceive(_ request: UNNotificationRequest,
                            withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void) {
        self.contentHandler = contentHandler
        bestAttemptContent = request.content.mutableCopy() as? UNNotificationContent

        // Download and attach image
        if let imageURL = request.content.userInfo["image_url"] as? String {
            guard let attachment = downloadAttachment(from: imageURL) else { return }
            bestAttemptContent?.attachments = [attachment]
        }

        contentHandler(bestAttemptContent ?? request.content)
    }
}
```

### Deliverability Best Practices

1. **Throttling**: Don't send >3 notifications per second to a single device
2. **Quiet hours**: Respect user-set do-not-disturb windows
3. **Badge management**: Clear badge on app open; set badge count on new items
4. **Topic messaging** (FCM): Use topics for fan-out instead of individual sends
5. **Device token refresh**: Handle `APNs token refresh` events; FCM `onTokenRefresh`
6. **Fallback**: Have in-app notification center as fallback when push fails

---

## 6. Performance Optimization

### React Native: Hermes + JSI

```tsx
// Enable Hermes (default in RN 0.76+)
// In android/app/build.gradle:
project.ext.react = [
  enableHermes: true
]

// For JSI native modules (instead of bridge):
import { TurboModule } from 'react-native';

// TurboModule spec in TypeScript:
import type { TurboModule } from 'react-native';

export interface Spec extends TurboModule {
  +startRecognition: (config: RecognitionConfig) => Promise<void>;
  +stopRecognition: () => Promise<void>;
  +getResult: () => Promise<RecognitionResult>;
}
```

### FlashList (RN) — Virtualized List

```tsx
import { FlashList } from '@shopify/flash-list';

<FlashList
  data={posts}
  estimatedItemSize={120}
  renderItem={({ item }) => <PostCard post={item} />}
  keyExtractor={(item) => item.id}
  // Performance features:
  overrideItemType={({ item }) => item.type}  // Typed items for optimization
/>
```

### Flutter: RepaintBoundary + Optimization

```dart
// RepaintBoundary isolates repaints
RepaintBoundary(
  child: AnimatedList(...)  // Only repaint when list changes
)

// Const widgets — compile-time optimization
const MyWidget({ required this.title })  // Mark all non-dynamic values const

// Image caching
CachedNetworkImage(
  imageUrl: 'https://...',
  placeholder: (context, url) => CircularProgressIndicator(),
  errorWidget: (context, url, error) => Icon(Icons.error),
  cacheManager: CacheManager(Config(
    stalePeriod: Duration(days: 7),
    maxNrOfCacheObjects: 200,
  )),
)

// Lazy loading with ListView.builder (not ListView)
ListView.builder(
  itemCount: 10000,
  itemBuilder: (context, index) => _buildItem(index),
)
```

---

## 7. CI/CD for Mobile

### Fastlane (iOS + Android)

```ruby
# Fastfile
lane :beta do
  # Cert signing
  match(
    type: 'appstore',
    readonly: true,
    app_identifier: 'com.mycompany.myapp'
  )

  # Build iOS
  increment_build_number(
    build_number: latest_testflight_build_number.to_i + 1
  )
  build_app(
    scheme: 'MyApp',
    export_method: 'app-store',
    output_directory: './build'
  )

  # Build Android
  gradle(
    task: 'assemble',
    flavor: 'production',
    build_type: 'release'
  )

  # Upload
  testflight(api_key: api_key)
  firebase_app_distribution(
    app: '1:xxx',
    groups: 'internal-testers'
  )

  # Slack notification
  slack(
    message: "Beta #{version} (#{build}) released",
    channel: '#mobile-releases'
  )
end
```

### GitHub Actions (RN)

```yaml
# .github/workflows/build.yml
name: Build

on:
  push:
    branches: [main]
  pull_request:

jobs:
  ios:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: cd ios && bundle install && bundle exec pod install
      - name: Build iOS
        run: xcodebuild -workspace ios/*.xcworkspace \
          -scheme MyApp \
          -configuration Debug \
          -destination 'platform=iOS Simulator,name=iPhone 15 Pro' \
          build CODE_SIGN_IDENTITY="" CODE_SIGNING_REQUIRED=NO
      - name: Build Android
        run: ./gradlew assembleDebug

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --coverage
      - uses: codecov/codecov-action@v3
        with: { file: ./coverage/lcov.info }
```

### Staged Rollouts

**iOS TestFlight**: External testers — can set percentage (10%, 25%, 50%, 100%)
**Google Play Console**: Closed testing tracks with percentage rollout

---

## 8. Security

### Biometric Auth

```dart
// Flutter
import 'package:local_auth/local_auth.dart';

final localAuth = LocalAuthentication();

Future<bool> canAuthenticate() async {
  final canCheck = await localAuth.canCheckBiometrics;
  final isDeviceSupported = await localAuth.isDeviceSupported();
  return canCheck && isDeviceSupported;
}

Future<bool> authenticate() async {
  return await localAuth.authenticate(
    localizedReason: 'Authenticate to access your data',
    options: const AuthenticationOptions(
      stickyAuth: true,
      biometricOnly: false,  // Fall back to device PIN
    ),
  );
}
```

```tsx
// React Native
import LocalAuthentication from 'react-native-local-authentication';

const result = await LocalAuthentication.authenticateAsync({
  reason: 'Please authenticate',
  fallbackToDevicePIN: true,
});
```

### Secure Storage

```dart
// Flutter
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const storage = FlutterSecureStorage(
  aOptions: AndroidOptions(encryptedSharedPreferences: true),
  iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
);

await storage.write(key: 'token', value: 'abc123');
final token = await storage.read(key: 'token');
```

```tsx
// React Native
import * as Keychain from 'react-native-keychain';

await Keychain.setGenericPassword('user', 'token', {
  service: 'myapp-auth',
  accessControl: Keychain.ACCESS_CONTROL.BIOMETRY_ANY,
  accessible: Keychain.ACCESSIBLE.WHEN_UNLOCKED_THIS_DEVICE_ONLY,
});

const credentials = await Keychain.getGenericPassword({ service: 'myapp-auth' });
```

### App Attest (iOS) — Anti-Tamper

```swift
// iOS App Attest
import DeviceCheck

func attestKey() async throws -> Data {
  let client = DCAppAttestService.shared
  guard client.isSupported else { throw AttestError.notSupported }

  let keyId = try await client.generateKey()
  let challenge = try await fetchChallengeFromServer()
  let attestObj = try await client.attestKey(
    keyId,
    clientDataHash: SHA256.hash(data: challenge)
  )
  return attestObj
}
```

### ProGuard / R8 (Android)

```gradle
// android/app/build.gradle
android {
  buildTypes {
    release {
      minifyEnabled true
      shrinkResources true
      proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
    }
  }
}
```

```proguard
# Obfuscate React Native JS bundle
-keep class com.facebook.react.** { *; }
-keep class com.facebook.hermes.** { *; }
-dontwarn com.facebook.**
```

---

## 9. Emerging Patterns (2025-2026)

### TurboModules / Bridgeless (RN)

New Architecture bridgeless mode: JS ↔ Native direct communication. All RN modules moving to TurboModule spec. Native modules written in C++ or Kotlin/Swift with TurboModule interface. Bridge fully deprecated.

### Gemini Nano / On-Device ML

Android AICore (Pixel 8+): Gemini Nano runs on-device for:
- Smart Reply in keyboard
- Summarization
- Context-aware suggestions

**RN on-device ML**:
```tsx
import { ModelScope } from '@modelScope/react-native';

// Use on-device model for privacy-sensitive inference
const result = await ModelScope.inference({
  model: 'text-classifier',
  input: userMessage,
});
```

### Foldables & Large Screens

Flutter: `MediaQuery.of(context).size` + `MediaQuery.of(context).displayFeatures` for fold-aware layouts. `PhysicalModel` for fold detection.

React Native: Same — `Dimensions.get('window')` but use `useWindowDimensions()` for dynamic updates.

### Wearables

- `flutter_wear_connector` for Android Wear / Wear OS
- watchOS complications with WidgetKit
- healthKit on iOS for fitness data

---

*Generated 2026-04-22 — Verify web search for latest tool versions and community updates*
