from src.cert import expire_static_attr, revoke_static_attr
from src.ta import attr_revoke, keygen, revoke_user, setup
from src.scheme import encrypt
from src.rsu import rsu_transform
from src.types import PolicyNotSatisfiedError, RevocationState, RevokedAttributeError, RevokedUserError


def test_user_revocation_blocks_transform():
    pp, msk = setup()
    bundle = keygen(pp, msk, uid='veh-004', static_attrs=['role:ambulance', 'dept:traffic'])
    state = revoke_user(RevocationState(), 'veh-004')
    ciphertext = encrypt(
        pp,
        message=b'hello-iov',
        static_policy=['role:ambulance', 'dept:traffic'],
        dynamic_policy=['region:r1', 'timeslot:t1'],
    )
    try:
        rsu_transform(
            pp,
            bundle.certificate,
            bundle.transform_key,
            ciphertext,
            state,
            context={'region:r1', 'timeslot:t1'},
        )
    except RevokedUserError:
        return
    raise AssertionError('expected revoked user to be rejected')


def test_static_attribute_revocation_blocks_transform():
    pp, msk = setup()
    bundle = keygen(pp, msk, uid='veh-005', static_attrs=['role:ambulance', 'dept:traffic'])
    state = attr_revoke(RevocationState(), 'veh-005', 'dept:traffic', revoke_type='static')
    ciphertext = encrypt(
        pp,
        message=b'hello-iov',
        static_policy=['role:ambulance', 'dept:traffic'],
        dynamic_policy=['region:r1', 'timeslot:t1'],
    )
    try:
        rsu_transform(
            pp,
            bundle.certificate,
            bundle.transform_key,
            ciphertext,
            state,
            context={'region:r1', 'timeslot:t1'},
        )
    except PolicyNotSatisfiedError:
        return
    raise AssertionError('expected revoked static attribute to fail')


def test_dynamic_attribute_revocation_blocks_transform():
    pp, msk = setup()
    bundle = keygen(pp, msk, uid='veh-006', static_attrs=['role:ambulance', 'dept:traffic'])
    state = attr_revoke(RevocationState(), 'veh-006', 'region:r1', revoke_type='dynamic')
    ciphertext = encrypt(
        pp,
        message=b'hello-iov',
        static_policy=['role:ambulance', 'dept:traffic'],
        dynamic_policy=['region:r1', 'timeslot:t1'],
    )
    try:
        rsu_transform(
            pp,
            bundle.certificate,
            bundle.transform_key,
            ciphertext,
            state,
            context={'region:r1', 'timeslot:t1'},
        )
    except RevokedAttributeError:
        return
    raise AssertionError('expected revoked dynamic attribute to fail')


def test_certificate_attribute_expiry_blocks_transform():
    pp, msk = setup()
    bundle = keygen(pp, msk, uid='veh-007', static_attrs=['role:ambulance', 'dept:traffic'])
    expire_static_attr(bundle.certificate, 'dept:traffic', expired_at=1)
    ciphertext = encrypt(
        pp,
        message=b'hello-iov',
        static_policy=['role:ambulance', 'dept:traffic'],
        dynamic_policy=['region:r1', 'timeslot:t1'],
    )
    try:
        rsu_transform(
            pp,
            bundle.certificate,
            bundle.transform_key,
            ciphertext,
            RevocationState(),
            context={'region:r1', 'timeslot:t1'},
            at_time=1,
        )
    except PolicyNotSatisfiedError:
        return
    raise AssertionError('expected expired certificate attribute to fail')


def test_certificate_attribute_removal_blocks_transform():
    pp, msk = setup()
    bundle = keygen(pp, msk, uid='veh-008', static_attrs=['role:ambulance', 'dept:traffic'])
    revoke_static_attr(bundle.certificate, 'dept:traffic')
    ciphertext = encrypt(
        pp,
        message=b'hello-iov',
        static_policy=['role:ambulance', 'dept:traffic'],
        dynamic_policy=['region:r1', 'timeslot:t1'],
    )
    try:
        rsu_transform(
            pp,
            bundle.certificate,
            bundle.transform_key,
            ciphertext,
            RevocationState(),
            context={'region:r1', 'timeslot:t1'},
        )
    except PolicyNotSatisfiedError:
        return
    raise AssertionError('expected removed certificate attribute to fail')
