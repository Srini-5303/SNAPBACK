// Sport-specific joint ROM requirements for the sport preview screen (Step 2).
// Sourced from Range of Joint Motion Evaluation Chart (clinical norms):
//   Shoulder flexion 150° | External rotation 90° | Internal rotation 70°
//   Elbow flexion 150°
//   Hip flexion 100° | Extension 30°
//   Knee flexion 150°
//   Ankle dorsiflexion 20° | Plantarflexion 40°
//   Wrist extension 60°
// All required values are ≤ clinical maximum.

export const sportBlueprints = {
  tennis: {
    name: 'Tennis',
    emoji: '🎾',
    tag: 'Upper body dominant',
    joints: {
      shoulder_flexion:           { required: 145, label: 'Shoulder Flexion' },
      shoulder_external_rotation: { required: 85,  label: 'Shoulder External Rotation' },
      thoracic_rotation:          { required: 40,  label: 'Thoracic Rotation' },
      hip_flexion:                { required: 90,  label: 'Hip Flexion' },
      hip_internal_rotation:      { required: 35,  label: 'Hip Internal Rotation' },
      knee_flexion:               { required: 125, label: 'Knee Flexion' },
      ankle_dorsiflexion:         { required: 20,  label: 'Ankle Dorsiflexion' },
      wrist_extension:            { required: 55,  label: 'Wrist Extension' },
    },
  },
  basketball: {
    name: 'Basketball',
    emoji: '🏀',
    tag: 'Vertical & lateral power',
    joints: {
      shoulder_flexion:           { required: 145, label: 'Shoulder Flexion' },
      shoulder_external_rotation: { required: 75,  label: 'Shoulder External Rotation' },
      hip_flexion:                { required: 95,  label: 'Hip Flexion' },
      hip_extension:              { required: 25,  label: 'Hip Extension' },
      knee_flexion:               { required: 130, label: 'Knee Flexion' },
      ankle_dorsiflexion:         { required: 20,  label: 'Ankle Dorsiflexion' },
      thoracic_rotation:          { required: 40,  label: 'Thoracic Rotation' },
      wrist_extension:            { required: 55,  label: 'Wrist Extension' },
    },
  },
  swimming: {
    name: 'Swimming',
    emoji: '🏊',
    tag: 'Shoulder & core mobility',
    joints: {
      shoulder_flexion:           { required: 148, label: 'Shoulder Flexion' },
      shoulder_extension:         { required: 45,  label: 'Shoulder Extension' },
      shoulder_external_rotation: { required: 85,  label: 'Shoulder External Rotation' },
      shoulder_internal_rotation: { required: 65,  label: 'Shoulder Internal Rotation' },
      thoracic_extension:         { required: 25,  label: 'Thoracic Extension' },
      hip_flexion:                { required: 90,  label: 'Hip Flexion' },
      ankle_plantarflexion:       { required: 38,  label: 'Ankle Plantarflexion' },
      ankle_dorsiflexion:         { required: 15,  label: 'Ankle Dorsiflexion' },
    },
  },
  crossfit: {
    name: 'CrossFit',
    emoji: '🏋️',
    tag: 'Full body overhead',
    joints: {
      shoulder_flexion:           { required: 148, label: 'Shoulder Flexion' },
      shoulder_external_rotation: { required: 85,  label: 'Shoulder External Rotation' },
      hip_flexion:                { required: 95,  label: 'Hip Flexion' },
      hip_external_rotation:      { required: 40,  label: 'Hip External Rotation' },
      knee_flexion:               { required: 140, label: 'Knee Flexion' },
      ankle_dorsiflexion:         { required: 20,  label: 'Ankle Dorsiflexion' },
      thoracic_extension:         { required: 25,  label: 'Thoracic Extension' },
      wrist_extension:            { required: 55,  label: 'Wrist Extension' },
    },
  },
  golf: {
    name: 'Golf',
    emoji: '⛳',
    tag: 'Rotational power',
    joints: {
      thoracic_rotation:          { required: 45,  label: 'Thoracic Rotation' },
      hip_internal_rotation:      { required: 40,  label: 'Hip Internal Rotation' },
      hip_external_rotation:      { required: 40,  label: 'Hip External Rotation' },
      shoulder_internal_rotation: { required: 55,  label: 'Shoulder Internal Rotation' },
      shoulder_external_rotation: { required: 75,  label: 'Shoulder External Rotation' },
      wrist_extension:            { required: 55,  label: 'Wrist Extension' },
      hip_flexion:                { required: 90,  label: 'Hip Flexion' },
      ankle_dorsiflexion:         { required: 18,  label: 'Ankle Dorsiflexion' },
    },
  },
  volleyball: {
    name: 'Volleyball',
    emoji: '🏐',
    tag: 'Overhead & explosive',
    joints: {
      shoulder_flexion:           { required: 148, label: 'Shoulder Flexion' },
      shoulder_external_rotation: { required: 85,  label: 'Shoulder External Rotation' },
      thoracic_extension:         { required: 25,  label: 'Thoracic Extension' },
      hip_flexion:                { required: 90,  label: 'Hip Flexion' },
      knee_flexion:               { required: 130, label: 'Knee Flexion' },
      ankle_dorsiflexion:         { required: 20,  label: 'Ankle Dorsiflexion' },
      wrist_extension:            { required: 55,  label: 'Wrist Extension' },
      thoracic_rotation:          { required: 35,  label: 'Thoracic Rotation' },
    },
  },
  baseball: {
    name: 'Baseball',
    emoji: '⚾',
    tag: 'Rotational & throwing',
    joints: {
      shoulder_external_rotation: { required: 90,  label: 'Shoulder External Rotation' },
      shoulder_internal_rotation: { required: 60,  label: 'Shoulder Internal Rotation' },
      shoulder_flexion:           { required: 145, label: 'Shoulder Flexion' },
      thoracic_rotation:          { required: 45,  label: 'Thoracic Rotation' },
      hip_internal_rotation:      { required: 35,  label: 'Hip Internal Rotation' },
      hip_external_rotation:      { required: 40,  label: 'Hip External Rotation' },
      elbow_flexion:              { required: 140, label: 'Elbow Flexion' },
      wrist_extension:            { required: 55,  label: 'Wrist Extension' },
    },
  },
  boxing: {
    name: 'Boxing',
    emoji: '🥊',
    tag: 'Upper body & core',
    joints: {
      shoulder_flexion:           { required: 145, label: 'Shoulder Flexion' },
      shoulder_external_rotation: { required: 70,  label: 'Shoulder External Rotation' },
      shoulder_internal_rotation: { required: 65,  label: 'Shoulder Internal Rotation' },
      thoracic_rotation:          { required: 45,  label: 'Thoracic Rotation' },
      hip_flexion:                { required: 90,  label: 'Hip Flexion' },
      hip_external_rotation:      { required: 35,  label: 'Hip External Rotation' },
      ankle_dorsiflexion:         { required: 20,  label: 'Ankle Dorsiflexion' },
      wrist_extension:            { required: 50,  label: 'Wrist Extension' },
    },
  },
};
